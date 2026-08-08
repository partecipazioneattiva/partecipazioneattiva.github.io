-- =====================================================================
-- AZZERA IL SONDAGGIO — si usa PRIMA di aprirlo alla gente
-- =====================================================================
-- Toglie i voti di prova e le impronte di chi ha provato, cosi' il
-- sondaggio parte da zero e chi ha fatto le prove puo' votare davvero.
-- Non tocca le tabelle ne' le funzioni: solo i numeri.
--
-- ⚠️ Da NON rilanciare a sondaggio aperto: cancellerebbe i voti veri.
-- =====================================================================

update sondaggio_conteggio set voti = 0;
delete from sondaggio_impronte;
delete from sondaggio_pendenti;

select tema, voti from sondaggio_conteggio order by ordine;
