-- =====================================================================
-- CORREZIONE 2 — 8 agosto 2026
-- =====================================================================
-- SINTOMO: il server riceveva
--     42883 "function digest(...) does not exist"
-- e nessuna mail partiva. Il sito invece riceveva «permission denied»:
-- due errori diversi, un guasto solo. Il controllo dei permessi avviene
-- PRIMA di entrare nella funzione, quindi chi non ha i permessi si ferma
-- sulla porta e non arriva mai a vedere il vero problema.
--
-- CAUSA: su Supabase l'estensione pgcrypto — quella che contiene digest(),
-- cioe' il rimescolamento sha256 dell'indirizzo — NON sta nel reparto
-- «public» ma in uno separato che si chiama «extensions». La funzione
-- aveva scritto «cerca in public» e basta, quindi digest() per lei non
-- esisteva.
--
-- RIMEDIO: si dice alla funzione di cercare anche in «extensions».
-- Una riga. Non si rifa' niente, non si perde niente.
-- =====================================================================

alter function sondaggio_registra(text, jsonb)
  set search_path = public, extensions;

-- e giusto per vedere nero su bianco dove abita davvero digest():
select n.nspname as reparto, p.proname as funzione
from pg_proc p join pg_namespace n on n.oid = p.pronamespace
where p.proname = 'digest';
