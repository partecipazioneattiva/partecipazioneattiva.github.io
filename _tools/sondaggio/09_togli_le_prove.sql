-- =====================================================================
-- TOGLIE SOLO I MIEI DUE VOTI DI PROVA — 9 agosto 2026
-- =====================================================================
-- NON azzera niente: i voti veri delle due persone che hanno risposto
-- stanotte restano dove sono. Toglie esattamente le due prove fatte da me
-- alle 08:50 e rimette a posto i conteggi dei temi che avevano segnato.
--
-- Le impronte non si possono leggere, ma si possono RICALCOLARE: sono
-- sha256(segreto + indirizzo), e gli indirizzi delle prove li conosco.
-- =====================================================================

do $$
declare
  v_pepe text := (select pepe from sondaggio_segreto where id = 1);
  v_uno  text;
  v_due  text;
begin
  v_uno := encode(extensions.digest(v_pepe || 'prova.sondaggio.uno@esempio.it', 'sha256'), 'hex');
  v_due := encode(extensions.digest(v_pepe || 'prova.sondaggio.due@esempio.it', 'sha256'), 'hex');

  -- prova 1: aveva segnato rc-auto e donna-a-napoli
  if exists (select 1 from sondaggio_impronte where impronta = v_uno) then
    update sondaggio_conteggio set voti = greatest(voti - 1, 0)
      where tema in ('rc-auto', 'donna-a-napoli');
    delete from sondaggio_impronte where impronta = v_uno;
  end if;

  -- prova 2: aveva segnato mappa
  if exists (select 1 from sondaggio_impronte where impronta = v_due) then
    update sondaggio_conteggio set voti = greatest(voti - 1, 0)
      where tema = 'mappa';
    delete from sondaggio_impronte where impronta = v_due;
  end if;
end $$;

select tema, voti, persone from sondaggio_risultati order by ordine;
