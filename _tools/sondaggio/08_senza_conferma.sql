-- =====================================================================
-- VIA LA CONFERMA VIA MAIL: chi vota, vota.
-- Partecipazione Attiva · 9 agosto 2026
-- =====================================================================
-- PERCHE'. Nelle prime ore due persone hanno votato davvero, le mail di
-- conferma sono state CONSEGNATE, e nessuna delle due ha cliccato. Due su
-- due. Il passaggio in piu' non proteggeva: perdeva voti.
--
-- COME FUNZIONA ORA. Si chiede l'indirizzo, ma non per scrivergli: serve
-- solo a riconoscere chi ha gia' risposto. L'indirizzo viene rimescolato
-- SUBITO col segreto e quello che resta e' un codice irreversibile.
-- L'indirizzo in chiaro non viene conservato MAI, nemmeno per un istante:
-- e' piu' riservato di prima, quando restava in attesa fino a 48 ore.
--
-- COSA SI PERDE, detto chiaro: non si verifica piu' che l'indirizzo sia
-- di chi lo scrive. Chi insiste puo' inventarne altri e votare piu' volte.
-- Il sondaggio e' INDICATIVO: dice dove va l'interesse, non proclama un
-- vincitore. Per decidere l'ordine di sei incontri e' il livello giusto.
-- =====================================================================

-- ---------------------------------------------------------------------
-- 1. I VOTI RIMASTI IN ATTESA SONO VOTI VERI: si contano adesso.
--    Sono persone che hanno risposto sul serio e non hanno cliccato.
-- ---------------------------------------------------------------------
do $$
declare r record;
begin
  for r in select * from sondaggio_pendenti loop
    if not exists (select 1 from sondaggio_impronte where impronta = r.impronta) then
      if coalesce(array_length(r.temi, 1), 0) > 0 then
        update sondaggio_conteggio set voti = voti + 1 where tema = any(r.temi);
      end if;
      if r.altro is not null then
        insert into sondaggio_proposte (testo) values (r.altro);
      end if;
      insert into sondaggio_impronte (impronta) values (r.impronta);
    end if;
  end loop;
  delete from sondaggio_pendenti;
end $$;

-- ---------------------------------------------------------------------
-- 2. LA FUNZIONE UNICA: riceve e conta, in un colpo solo.
--    La chiama SOLO il server: se potesse chiamarla il sito, chiunque
--    potrebbe farlo da una finestra del browser mille volte di fila.
-- ---------------------------------------------------------------------
create or replace function sondaggio_vota(p_email text, p_temi jsonb, p_altro text)
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
  if v_altro is not null then
    insert into sondaggio_proposte (testo) values (v_altro);
  end if;
  insert into sondaggio_impronte (impronta) values (v_impronta);

  select jsonb_agg(jsonb_build_object('tema', tema, 'voti', voti) order by ordine)
    into v_ris from sondaggio_conteggio;
  select count(*) into v_persone from sondaggio_impronte;

  return jsonb_build_object('esito', 'contato',
                            'risultati', v_ris,
                            'persone', v_persone,
                            'proposta', v_altro);  -- la legge SOLO il server, per spedirla
end
$$;
revoke all on function sondaggio_vota(text, jsonb, text) from public, anon, authenticated;
grant execute on function sondaggio_vota(text, jsonb, text) to service_role;

-- ---------------------------------------------------------------------
-- 3. PULIZIA: la conferma non serve piu'.
--    La tabella dei voti in attesa nemmeno: l'indirizzo non ci passa piu'.
-- ---------------------------------------------------------------------
drop function if exists sondaggio_conferma(uuid);
drop function if exists sondaggio_registra(text, jsonb, text);
drop function if exists sondaggio_registra(text, jsonb);
drop table if exists sondaggio_pendenti;

notify pgrst, 'reload schema';

select tema, voti, persone from sondaggio_risultati order by ordine;
