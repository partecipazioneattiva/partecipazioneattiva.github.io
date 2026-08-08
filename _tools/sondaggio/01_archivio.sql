-- =====================================================================
-- SONDAGGIO «I SEI APPUNTAMENTI DI SETTEMBRE»
-- Partecipazione Attiva · 8 agosto 2026
-- =====================================================================
-- Si incolla UNA VOLTA SOLA nel pannello Supabase → SQL Editor → Run.
--
-- NON contiene nessuna chiave e nessuna password: il segreto con cui si
-- rimescolano gli indirizzi se lo genera il database da solo, e non esce
-- mai da li'. Non lo conosce nemmeno chi ha scritto questo file.
--
-- COSA SI CONSERVA, E PER QUANTO:
--   · i numeri dei voti                        → per sempre (sono anonimi)
--   · un'impronta illeggibile di chi ha votato → per la durata del sondaggio
--   · l'indirizzo email in chiaro              → SOLO fino alla conferma,
--                                                 e comunque max 48 ore
-- Dopo la conferma l'indirizzo viene CANCELLATO. Resta l'impronta, che
-- serve a dire «questo indirizzo ha gia' votato» e non si puo' ricondurre
-- a nessuno: e' un sha256 con un segreto che sta solo sul server.
-- =====================================================================

create extension if not exists pgcrypto;

-- ---------------------------------------------------------------------
-- 1. IL SEGRETO. Lo fabbrica il database, 32 byte a caso.
-- ---------------------------------------------------------------------
create table if not exists sondaggio_segreto (
  id   int  primary key default 1,
  pepe text not null default encode(gen_random_bytes(32), 'hex'),
  constraint una_sola_riga check (id = 1)
);
insert into sondaggio_segreto (id) values (1) on conflict (id) do nothing;
alter table sondaggio_segreto enable row level security;
-- nessuna policy = nessuno lo legge dal sito. Solo le funzioni qui sotto.

-- ---------------------------------------------------------------------
-- 2. I SEI TEMI E I LORO VOTI. Sono quelli dello spot di settembre.
-- ---------------------------------------------------------------------
create table if not exists sondaggio_conteggio (
  tema   text     primary key,
  ordine smallint not null,
  voti   integer  not null default 0
);
insert into sondaggio_conteggio (tema, ordine) values
  ('ape',              1),   -- APE, l'Assemblea Popolare Ecumenica — Angelo Nicotra
  ('mappa',            2),   -- La Mappa dei cittadini attivi — Daniele Tandura
  ('legge-elettorale', 3),   -- La legge elettorale — Luigi Spanu (in diretta)
  ('rc-auto',          4),   -- RC Auto — Paolo Neri (in diretta)
  ('arte-del-dono',    5),   -- L'arte del dono — Stefano Piva
  ('donna-a-napoli',   6)    -- Essere donna a Napoli — Rosa Ugon
on conflict (tema) do nothing;
alter table sondaggio_conteggio enable row level security;

-- ---------------------------------------------------------------------
-- 3. CHI HA GIA' VOTATO — senza sapere chi e'.
-- ---------------------------------------------------------------------
create table if not exists sondaggio_impronte (
  impronta  text        primary key,
  creato_il timestamptz not null default now()
);
alter table sondaggio_impronte enable row level security;

-- ---------------------------------------------------------------------
-- 4. I VOTI IN ATTESA DI CONFERMA.
--    E' l'unico posto dove l'indirizzo esiste in chiaro, e ci resta
--    poche ore: serve solo a mandargli la mail.
-- ---------------------------------------------------------------------
create table if not exists sondaggio_pendenti (
  token     uuid        primary key default gen_random_uuid(),
  temi      text[]      not null,
  email     text        not null,
  impronta  text        not null,
  creato_il timestamptz not null default now()
);
create index if not exists sondaggio_pendenti_creato_idx
  on sondaggio_pendenti (creato_il);
alter table sondaggio_pendenti enable row level security;

-- ---------------------------------------------------------------------
-- 5. QUELLO CHE IL SITO PUO' LEGGERE: soltanto i numeri.
-- ---------------------------------------------------------------------
create or replace view sondaggio_risultati as
  select tema,
         ordine,
         voti,
         (select coalesce(sum(voti), 0) from sondaggio_conteggio) as totale
  from sondaggio_conteggio
  order by ordine;
grant select on sondaggio_risultati to anon, authenticated;

-- ---------------------------------------------------------------------
-- 6. REGISTRA UN VOTO IN ATTESA.
--    La chiama SOLO la funzione del server (service_role): se potesse
--    chiamarla il sito, chiunque otterrebbe il codice di conferma senza
--    ricevere la mail, e la verifica dell'indirizzo non varrebbe niente.
-- ---------------------------------------------------------------------
create or replace function sondaggio_registra(p_email text, p_temi text[])
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  v_email    text;
  v_impronta text;
  v_token    uuid;
  v_validi   int;
begin
  -- pulizia di routine: i non confermati oltre 48 ore spariscono
  delete from sondaggio_pendenti where creato_il < now() - interval '48 hours';

  v_email := lower(btrim(coalesce(p_email, '')));
  if v_email !~ '^[^@[:space:]]+@[^@[:space:]]+\.[a-z]{2,}$' then
    return jsonb_build_object('esito', 'email_non_valida');
  end if;

  if p_temi is null or array_length(p_temi, 1) is null
     or array_length(p_temi, 1) > 6 then
    return jsonb_build_object('esito', 'temi_non_validi');
  end if;

  select count(*) into v_validi
    from sondaggio_conteggio where tema = any(p_temi);
  if v_validi <> array_length(p_temi, 1) then
    return jsonb_build_object('esito', 'temi_non_validi');
  end if;

  v_impronta := encode(digest((select pepe from sondaggio_segreto where id = 1)
                              || v_email, 'sha256'), 'hex');

  if exists (select 1 from sondaggio_impronte where impronta = v_impronta) then
    return jsonb_build_object('esito', 'gia_votato');
  end if;

  -- Se ha appena chiesto, non si rimanda un'altra mail: serve a impedire
  -- che qualcuno riempia la casella di un altro riscrivendo il suo indirizzo.
  if exists (select 1 from sondaggio_pendenti
             where impronta = v_impronta
               and creato_il > now() - interval '10 minutes') then
    return jsonb_build_object('esito', 'gia_inviata');
  end if;

  -- se aveva gia' chiesto tempo fa e non ha confermato, si sostituisce
  delete from sondaggio_pendenti where impronta = v_impronta;

  insert into sondaggio_pendenti (temi, email, impronta)
  values (p_temi, v_email, v_impronta)
  returning token into v_token;

  return jsonb_build_object('esito', 'da_confermare', 'token', v_token);
end
$$;
revoke all on function sondaggio_registra(text, text[]) from public, anon, authenticated;
-- ...ma il server SI': e' lui l'unico che deve poterla usare. Senza questa riga
-- la funzione del sondaggio riceve «permission denied» e non parte nessuna mail.
grant execute on function sondaggio_registra(text, text[]) to service_role;

-- ---------------------------------------------------------------------
-- 7. CONFERMA IL VOTO.
--    Questa la puo' chiamare il sito, perche' serve il codice arrivato
--    per posta: e' un numero a caso su 2^122 possibilita', non si indovina.
--    E' il momento in cui l'indirizzo VIENE CANCELLATO.
-- ---------------------------------------------------------------------
create or replace function sondaggio_conferma(p_token uuid)
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  r         sondaggio_pendenti%rowtype;
  v_ris     jsonb;
  v_totale  bigint;
begin
  delete from sondaggio_pendenti where creato_il < now() - interval '48 hours';

  select * into r from sondaggio_pendenti where token = p_token;
  if not found then
    return jsonb_build_object('esito', 'scaduto');
  end if;

  if exists (select 1 from sondaggio_impronte where impronta = r.impronta) then
    delete from sondaggio_pendenti where token = p_token;
    return jsonb_build_object('esito', 'gia_votato');
  end if;

  update sondaggio_conteggio set voti = voti + 1 where tema = any(r.temi);
  insert into sondaggio_impronte (impronta) values (r.impronta);

  -- ⬇️ QUI l'indirizzo email sparisce, e non e' piu' recuperabile
  delete from sondaggio_pendenti where token = p_token;

  select jsonb_agg(jsonb_build_object('tema', tema, 'voti', voti) order by ordine),
         coalesce(sum(voti), 0)
    into v_ris, v_totale
    from sondaggio_conteggio;

  return jsonb_build_object('esito', 'contato',
                            'risultati', v_ris,
                            'totale', v_totale,
                            'scelti', r.temi);
end
$$;
grant execute on function sondaggio_conferma(uuid) to anon, authenticated;

-- =====================================================================
-- FINE. Da qui in poi il sondaggio ha dove scrivere.
-- Per chiuderlo, un giorno:   drop table sondaggio_impronte;
-- (i numeri restano, le impronte spariscono)
-- =====================================================================
