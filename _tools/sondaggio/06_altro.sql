-- =====================================================================
-- «ALTRO» — chi vota puo' scrivere cosa ha a cuore
-- Partecipazione Attiva · 8 agosto 2026
-- =====================================================================
-- Si incolla nell'SQL Editor e si preme Run. Non tocca i voti gia' presi.
--
-- COME E' PENSATO, e perche':
--
-- Il testo libero e' l'unico punto in cui possono finire dati personali
-- senza che li chiediamo noi (nomi, malattie, indirizzi). Quindi:
--
--   · si conserva STACCATO dal voto e dall'indirizzo — nella tabella
--     sondaggio_proposte non c'e' nessun collegamento a chi l'ha scritto,
--     nemmeno l'impronta. Non e' ricostruibile da nessuno, noi compresi;
--   · si conserva SOLO DOPO la conferma via mail, cosi' non raccogliamo
--     lo sfogo di chi passa, scrive e non conferma;
--   · non si pubblica niente in automatico: le frasi le legge il movimento.
-- =====================================================================

-- ---------------------------------------------------------------------
-- 1. Dove finiscono le frasi. Nessun legame con nessuno.
-- ---------------------------------------------------------------------
create table if not exists sondaggio_proposte (
  id        bigserial   primary key,
  testo     text        not null,
  creato_il timestamptz not null default now()
);
alter table sondaggio_proposte enable row level security;
-- nessuna policy: dal sito non si legge e non si scrive. Si guardano dal
-- pannello, in Table Editor.

-- ---------------------------------------------------------------------
-- 2. Il voto in attesa si porta dietro anche la frase, finche' non e'
--    confermato. Poi la frase si trasferisce e la riga sparisce.
-- ---------------------------------------------------------------------
alter table sondaggio_pendenti add column if not exists altro text;

-- ---------------------------------------------------------------------
-- 3. REGISTRA — ora accetta anche la frase.
--    Via la versione a due argomenti, altrimenti restano due funzioni con
--    lo stesso nome e il ponte non sa quale scegliere.
-- ---------------------------------------------------------------------
drop function if exists sondaggio_registra(text, jsonb);

create or replace function sondaggio_registra(p_email text, p_temi jsonb, p_altro text)
returns jsonb
language plpgsql
security definer
set search_path = public, extensions   -- extensions serve per digest()
as $$
declare
  v_email    text;
  v_temi     text[];
  v_altro    text;
  v_impronta text;
  v_token    uuid;
  v_validi   int;
  v_quanti   int;
begin
  delete from sondaggio_pendenti where creato_il < now() - interval '48 hours';

  v_email := lower(btrim(coalesce(p_email, '')));
  if v_email !~ '^[^@[:space:]]+@[^@[:space:]]+\.[a-z]{2,}$' then
    return jsonb_build_object('esito', 'email_non_valida');
  end if;

  -- la frase: ripulita, e comunque non piu' lunga di 400 caratteri
  v_altro := nullif(btrim(coalesce(p_altro, '')), '');
  if v_altro is not null then
    v_altro := left(v_altro, 400);
  end if;

  if p_temi is null or jsonb_typeof(p_temi) <> 'array' then
    return jsonb_build_object('esito', 'temi_non_validi');
  end if;
  v_temi := array(select jsonb_array_elements_text(p_temi));
  v_quanti := coalesce(array_length(v_temi, 1), 0);

  -- si accetta anche chi non segna nessun tema ma scrive qualcosa
  if v_quanti = 0 and v_altro is null then
    return jsonb_build_object('esito', 'temi_non_validi');
  end if;
  if v_quanti > 6 then
    return jsonb_build_object('esito', 'temi_non_validi');
  end if;

  if v_quanti > 0 then
    select count(*) into v_validi
      from sondaggio_conteggio where tema = any(v_temi);
    if v_validi <> v_quanti then
      return jsonb_build_object('esito', 'temi_non_validi');
    end if;
  end if;

  v_impronta := encode(digest((select pepe from sondaggio_segreto where id = 1)
                              || v_email, 'sha256'), 'hex');

  if exists (select 1 from sondaggio_impronte where impronta = v_impronta) then
    return jsonb_build_object('esito', 'gia_votato');
  end if;

  if exists (select 1 from sondaggio_pendenti
             where impronta = v_impronta
               and creato_il > now() - interval '10 minutes') then
    return jsonb_build_object('esito', 'gia_inviata');
  end if;

  delete from sondaggio_pendenti where impronta = v_impronta;

  insert into sondaggio_pendenti (temi, email, impronta, altro)
  values (v_temi, v_email, v_impronta, v_altro)
  returning token into v_token;

  return jsonb_build_object('esito', 'da_confermare', 'token', v_token);
end
$$;
revoke all on function sondaggio_registra(text, jsonb, text) from public, anon, authenticated;
grant execute on function sondaggio_registra(text, jsonb, text) to service_role;

-- ---------------------------------------------------------------------
-- 4. CONFERMA — e' qui che la frase si stacca da chi l'ha scritta.
-- ---------------------------------------------------------------------
create or replace function sondaggio_conferma(p_token uuid)
returns jsonb
language plpgsql
security definer
set search_path = public, extensions
as $$
declare
  r        sondaggio_pendenti%rowtype;
  v_ris    jsonb;
  v_totale bigint;
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

  if coalesce(array_length(r.temi, 1), 0) > 0 then
    update sondaggio_conteggio set voti = voti + 1 where tema = any(r.temi);
  end if;

  -- ⬇️ la frase entra qui SENZA impronta e SENZA indirizzo: da questo
  --    momento non e' piu' riconducibile a nessuno
  if r.altro is not null then
    insert into sondaggio_proposte (testo) values (r.altro);
  end if;

  insert into sondaggio_impronte (impronta) values (r.impronta);
  delete from sondaggio_pendenti where token = p_token;

  select jsonb_agg(jsonb_build_object('tema', tema, 'voti', voti) order by ordine),
         coalesce(sum(voti), 0)
    into v_ris, v_totale
    from sondaggio_conteggio;

  return jsonb_build_object('esito', 'contato',
                            'risultati', v_ris,
                            'totale', v_totale,
                            'scelti', r.temi,
                            'proposta', r.altro);   -- la legge SOLO il server, per spedirla al movimento
end
$$;

-- Da adesso la conferma passa dal server, non piu' dal sito: e' il server
-- che deve leggere la frase per mandarvela per posta. Il sito non la vede
-- e non puo' vederla.
revoke all on function sondaggio_conferma(uuid) from public, anon, authenticated;
grant execute on function sondaggio_conferma(uuid) to service_role;

notify pgrst, 'reload schema';

-- =====================================================================
-- DOVE SI LEGGONO LE FRASI
--   pannello → Table Editor → sondaggio_proposte
-- Sono in ordine di arrivo, senza nome e senza indirizzo.
-- =====================================================================
