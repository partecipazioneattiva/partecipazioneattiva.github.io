-- =====================================================================
-- LE PERCENTUALI VANNO CALCOLATE SULLE PERSONE, NON SULLE PREFERENZE
-- Partecipazione Attiva · 8 agosto 2026
-- =====================================================================
-- L'ERRORE: la vista dichiarava come «totale» la SOMMA delle preferenze.
-- Con la scelta multipla e' una misura sbagliata: se dieci persone segnano
-- tre temi a testa, il totale fa 30 e nessun tema puo' superare il 33%
-- anche se l'avessero scelto tutte e dieci. Il numero direbbe «poco
-- interesse» dove c'e' unanimita'.
--
-- LA MISURA GIUSTA: quante persone su quante hanno indicato quel tema.
-- Le persone che hanno confermato sono le righe di sondaggio_impronte:
-- una a testa, per costruzione.
--
-- Nota: chi scrive SOLO nella casella libera senza segnare temi conta
-- come persona che ha risposto. E' giusto: ha risposto, e il fatto che
-- nessuno dei sei l'abbia convinta e' essa stessa un'informazione.
-- =====================================================================

create or replace view sondaggio_risultati as
  select tema,
         ordine,
         voti,
         (select count(*) from sondaggio_impronte)        as persone,
         (select coalesce(sum(voti), 0)
            from sondaggio_conteggio)                     as preferenze
  from sondaggio_conteggio
  order by ordine;

grant select on sondaggio_risultati to anon, authenticated;

notify pgrst, 'reload schema';

select tema, voti, persone, preferenze from sondaggio_risultati order by ordine;
