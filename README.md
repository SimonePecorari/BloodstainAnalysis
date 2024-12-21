# Analisi delle Acquisizioni

Questo progetto si concentra sull'elaborazione e analisi dei dati ottenuti da immagini in formato HDR e PNG. Si esegue una serie di operazioni per estrapolare informazioni utili dai campioni acquisiti nel tempo e si fa un'analisi qualitativa dei campioni di sangue in relazione alle sostanze come:
- Ketchup
- Sangue finto
- Alchermes

I tool impiegati sono

## Dati in Input

I dati in input per il codice sono i file:

- **HDR**: file contenente i dati spettrali del campione.
- **PNG**: immagine rappresentante il campione a un determinato istante di tempo.

## Macro-Steps Eseguiti

Il codice esegue i seguenti passaggi principali:

1. **Selezione automatica tramite ROI (Region of Interest)**:
   - Viene selezionata automaticamente una porzione di pixel per l'analisi.
   
2. **Calcolo delle medie degli spettri per campioni giornalieri**:
   - Calcolo della media degli spettri per ogni sostanza su base giornaliera.
   
3. **Plot dei grafici di riflettanza media**:
   - Creazione di grafici che mostrano la riflettanza media per ogni sostanza analizzata.

4. **Confronto nel tempo**:
   - Viene eseguito un confronto delle riflettanze nel tempo per osservare eventuali variazioni.

5. **Variazione dei punti caratteristici e pendenza della curva del sangue**:
   - Analisi della variazione nei punti caratteristici e nella pendenza della curva di riflettanza del sangue nel tempo.

## Uso delle Maschere nell'Elaborazione delle Immagini

L'elaborazione delle immagini a tre canali (BGR - Blue, Green, Red) viene gestita utilizzando maschere per isolare porzioni di colore specifiche. I valori di ciascun canale BGR nella maschera vengono interpretati come binari. L'uso delle maschere BGR offre diversi vantaggi:

- Conservazione delle informazioni sul colore.
- Utilizzo dei dati relativi all'immagine originale per applicare filtri o sovrapporre elementi.

Nel codice sono incluse delle righe che definiscono maschere per l'immagine, applicando limiti specifici al colore rosso. Le due maschere generate vengono successivamente combinate per ottenere un'unica maschera applicata all'immagine analizzata.

## Conclusioni

Il flusso di lavoro descritto consente di analizzare e confrontare i dati spettrali e visivi dei campioni nel tempo, evidenziando le variazioni nei parametri di riflettanza e nei punti caratteristici delle curve di riflettanza.
