-- =====================================================================
-- TOGLIE LA PROVA DELLA "PRIMA SCELTA" - 9 agosto 2026, 13:50
-- =====================================================================
-- NON azzera niente. Leva un solo voto: quello che ho mandato io per
-- verificare che la catena nuova (sito -> funzione -> archivio) contasse
-- davvero anche la prima scelta. Aveva segnato "ape" e "mappa", con
-- "mappa" come tema che pesa di piu'.
--
-- Le impronte non si possono leggere, ma si possono RICALCOLARE: sono
-- sha256(segreto + indirizzo), e l'indirizzo della prova lo conosco.
-- Stesso metodo di 09_togli_le_prove.sql.
--
-- Si puo' rilanciare senza danni: se la prova non c'e' piu', non fa nulla.
-- =====================================================================

do $$
declare
  v_pepe   text := (select pepe from sondaggio_segreto where id = 1);
  v_prova  text;
begin
  v_prova := encode(extensions.digest(v_pepe || 'prova.prima.scelta@esempio.it',
                                      'sha256'), 'hex');

  if exists (select 1 from sondaggio_impronte where impronta = v_prova) then
    update sondaggio_conteggio set voti = greatest(voti - 1, 0)
      where tema in ('ape', 'mappa');
    update sondaggio_conteggio set voti_primo = greatest(voti_primo - 1, 0)
      where tema = 'mappa';
    delete from sondaggio_impronte where impronta = v_prova;
  end if;
end $$;

select tema, voti, voti_primo, persone, prime_scelte
  from sondaggio_risultati order by ordine;
