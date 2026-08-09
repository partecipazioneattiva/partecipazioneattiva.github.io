-- =====================================================================
-- LA PRIMA SCELTA: "e se dovessi sceglierne uno solo, quale?"
-- Partecipazione Attiva - 9 agosto 2026
-- =====================================================================
-- PERCHE'. Le sei caselle libere dicono a quali temi la gente e'
-- interessata, ma non li mettono in ordine: nei primi giorni davano
-- 3-3-3-3-2-2, cioe' niente. Paolo Walter l'ha segnalato per iscritto.
--
-- La sua proposta era far numerare tutti e sei da 1 a 6. Scartata, e il
-- motivo sta nei numeri: le linee guida per i sondaggi di partecipazione
-- civica raccomandano l'ordinamento solo sotto le quattro-cinque voci, e
-- il 68% del nostro pubblico arriva da telefono, dove ordinare sei voci
-- e' il punto in cui si chiude la pagina. Chi abbandona non lascia una
-- risposta parziale: non lascia niente.
--
-- La domanda singola da' la stessa graduatoria - si contano le prime
-- scelte - al prezzo di UN tocco. E compare solo a chi ha segnato almeno
-- due temi: sotto, la risposta e' gia' ovvia e la domanda non si vede.
--
-- SI PUO' RILANCIARE SENZA DANNI: e' scritto per non rifare due volte le
-- stesse cose.
-- =====================================================================

-- ---------------------------------------------------------------------
-- 1. UN SECONDO CONTATORE, accanto a quello dei temi.
--    Restano due numeri distinti: "quanti lo vogliono" e "quanti lo
--    vogliono per primo". Servono a due domande diverse.
-- ---------------------------------------------------------------------
alter table sondaggio_conteggio
  add column if not exists voti_primo integer not null default 0;

-- ---------------------------------------------------------------------
-- 2. LA VISTA PUBBLICA: le colonne nuove vanno IN FONDO.
--    create or replace view accetta colonne aggiunte alla fine, non in
--    mezzo: cambiarne l'ordine darebbe "cannot change name of view
--    column".
-- ---------------------------------------------------------------------
create or replace view sondaggio_risultati as
  select tema,
         ordine,
         voti,
         (select count(*) from sondaggio_impronte)         as persone,
         (select coalesce(sum(voti), 0)
            from sondaggio_conteggio)                      as preferenze,
         voti_primo,
         (select coalesce(sum(voti_primo), 0)
            from sondaggio_conteggio)                      as prime_scelte
  from sondaggio_conteggio
  order by ordine;

grant select on sondaggio_risultati to anon, authenticated;

-- ---------------------------------------------------------------------
-- 3. LA FUNZIONE, con un argomento in piu'.
--    p_primo puo' essere nullo: la domanda si puo' saltare, e saltarla
--    non deve mai far perdere il voto sui temi.
-- ---------------------------------------------------------------------
create or replace function sondaggio_vota(p_email text, p_temi jsonb,
                                          p_altro text, p_primo text)
returns jsonb
language plpgsql
security definer
set search_path = public, extensions   -- extensions serve per digest()
as $$
declare
  v_email    text;
  v_temi     text[];
  v_altro    text;
  v_primo    text;
  v_impronta text;
  v_validi   int;
  v_quanti   int;
  v_ris      jsonb;
  v_persone  bigint;
begin
  v_email := lower(btrim(coalesce(p_email, '')));
  if v_email !~ '^[^@[:space:]]+@[^@[:space:]]+\.[a-z]{2,}$' then
    return jsonb_build_object('esito', 'email_non_valida');
  end if;

  v_altro := nullif(btrim(coalesce(p_altro, '')), '');
  if v_altro is not null then
    v_altro := left(v_altro, 400);
  end if;

  if p_temi is null or jsonb_typeof(p_temi) <> 'array' then
    return jsonb_build_object('esito', 'temi_non_validi');
  end if;
  v_temi := array(select jsonb_array_elements_text(p_temi));
  v_quanti := coalesce(array_length(v_temi, 1), 0);

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

  -- la prima scelta, se c'e', dev'essere uno dei sei E fra quelli segnati:
  -- "quale pesa di piu'" ha senso solo dentro cio' che si e' gia' scelto.
  --
  -- ⚠️ NON e' un ordine di uscita, e non va mai presentata come tale: i tempi
  -- di preparazione di ciascun incontro non si conoscono ancora (ordine di
  -- Fernando, 9 agosto 2026). Dice quale tema pesa di piu', e basta.
  v_primo := nullif(btrim(coalesce(p_primo, '')), '');
  if v_primo is not null and not (v_primo = any(v_temi)) then
    return jsonb_build_object('esito', 'primo_non_valido');
  end if;

  -- ⬇️ QUI l'indirizzo diventa un codice irreversibile e sparisce.
  --    Da questa riga in poi non esiste piu' da nessuna parte.
  v_impronta := encode(digest((select pepe from sondaggio_segreto where id = 1)
                              || v_email, 'sha256'), 'hex');

  if exists (select 1 from sondaggio_impronte where impronta = v_impronta) then
    return jsonb_build_object('esito', 'gia_votato');
  end if;

  if v_quanti > 0 then
    update sondaggio_conteggio set voti = voti + 1 where tema = any(v_temi);
  end if;
  if v_primo is not null then
    update sondaggio_conteggio set voti_primo = voti_primo + 1 where tema = v_primo;
  end if;
  if v_altro is not null then
    insert into sondaggio_proposte (testo) values (v_altro);
  end if;
  insert into sondaggio_impronte (impronta) values (v_impronta);

  select jsonb_agg(jsonb_build_object('tema', tema, 'voti', voti,
                                      'voti_primo', voti_primo) order by ordine)
    into v_ris from sondaggio_conteggio;
  select count(*) into v_persone from sondaggio_impronte;

  return jsonb_build_object('esito', 'contato',
                            'risultati', v_ris,
                            'persone', v_persone,
                            'proposta', v_altro);  -- la legge SOLO il server
end
$$;

revoke all on function sondaggio_vota(text, jsonb, text, text)
  from public, anon, authenticated;
grant execute on function sondaggio_vota(text, jsonb, text, text) to service_role;

-- ---------------------------------------------------------------------
-- 4. VIA LA VERSIONE A TRE ARGOMENTI.
--    Se restasse, con un argomento in piu' di default la chiamata
--    diventerebbe ambigua e PostgREST risponderebbe 42883.
-- ---------------------------------------------------------------------
drop function if exists sondaggio_vota(text, jsonb, text);

notify pgrst, 'reload schema';

select tema, voti, voti_primo, persone, prime_scelte
  from sondaggio_risultati order by ordine;
