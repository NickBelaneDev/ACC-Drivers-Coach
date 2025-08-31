class CornerPerformanceScorer:
    """
    Berechnet pro Kurve einen vergleichbaren Performance-Score (in %) und Teil-Scores für
    Bremsen, Apex, Exit auf Basis von g_lat und g_long sowie optional SPEED/BRAKE/THROTTLE.

    Erwartung an corner_df:
      - Enthält die Telemetriesamples NUR für EINE Kurve (Start bis End der Kurve).
      - Idealerweise auf gleichmäßiges Distanzraster resampelt (z.B. 1 m).
      - Übliche Spaltennamen werden automatisch erkannt (siehe _auto_map_columns).

    Haupt-Idee:
      - G_ges(t) = sqrt(g_lat(t)^2 + g_long(t)^2)
      - Score_total = Integral(G_ges über Kurve) relativ zur Referenz (in %)
      - Teil-Scores:
          * Brems-Score: Integral der Verzögerung (g_long < 0) VOR Apex relativ Ref (%)
          * Apex-Score: mittleres g_lat um den Apex herum relativ Ref (%)
          * Exit-Score: Integral der Beschleunigung (g_long > 0) NACH Apex relativ Ref (%)
      - Optional: Entry/Apex/Exit-Speed als Prozent relativ zur Ref.

    Rückgabe: Dictionary mit Prozentwerten und ein paar Rohwerten für Debug/Weiterverwendung.
    """
    def __init__(self):
        pass
