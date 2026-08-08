-- =====================================================================
-- CORREZIONE — 8 agosto 2026, subito dopo la prima prova
-- =====================================================================
-- SINTOMO: la funzione del server riceveva
--     404 {"code":"42883","hint":"No function matches the given name
--          and argument type..."}
-- e quindi nessuna mail partiva.
--
-- CAUSA: l'elenco dei temi viaggiava come lista di testo (text[]). Il
-- ponte fra le funzioni del server e l'archivio (PostgREST) non sempre
-- riesce ad abbinare una lista JSON a quel tipo: dipende da com'e' messa
-- la sua memoria interna dei tipi, e quando non ci riesce dice che la
-- funzione «non esiste».
--
-- RIMEDIO: i temi arrivano come JSON (jsonb), che quel ponte gestisce
-- sempre allo stesso modo, e diventano una lista una volta dentro. La
-- funzione del server NON va rifatta: manda gia' esattamente questo.
-- =====================================================================

-- via la versione vecchia, altrimenti restano due funzioni con lo stesso
-- nome e il ponte non sa quale scegliere
drop function if exists sondaggio_registra(text, text[]);

create or replace function sondaggio_registra(p_email text, p_temi jsonb)
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  v_email    text;
  v_temi     text[];
  v_impronta text;
  v_token    uuid;
  v_validi   int;
begin
  delete from sondaggio_pendenti where creato_il < now() - interval '48 hours';

  v_email := lower(btrim(coalesce(p_email, '')));
  if v_email !~ '^[^@[:space:]]+@[^@[:space:]]+\.[a-z]{2,}$' then
    return jsonb_build_object('esito', 'email_non_valida');
  end if;

  -- da JSON a lista
  if p_temi is null or jsonb_typeof(p_temi) <> 'array' then
    return jsonb_build_object('esito', 'temi_non_validi');
  end if;
  v_temi := array(select jsonb_array_elements_text(p_temi));

  if array_length(v_temi, 1) is null or array_length(v_temi, 1) > 6 then
    return jsonb_build_object('esito', 'temi_non_validi');
  end if;

  select count(*) into v_validi
    from sondaggio_conteggio where tema = any(v_temi);
  if v_validi <> array_length(v_temi, 1) then
    return jsonb_build_object('esito', 'temi_non_validi');
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

  insert into sondaggio_pendenti (temi, email, impronta)
  values (v_temi, v_email, v_impronta)
  returning token into v_token;

  return jsonb_build_object('esito', 'da_confermare', 'token', v_token);
end
$$;

-- il sito NON deve poterla chiamare: otterrebbe il codice di conferma
-- senza ricevere la mail, e la verifica dell'indirizzo non varrebbe niente
revoke all on function sondaggio_registra(text, jsonb) from public, anon, authenticated;
-- il server si', ed e' l'unico
grant execute on function sondaggio_registra(text, jsonb) to service_role;

-- e si rinfresca la memoria dei tipi del ponte, cosi' vede subito la nuova
notify pgrst, 'reload schema';
