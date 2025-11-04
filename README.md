# Shiny Apps Portfolio

This repository contains examples of Shiny dashboards I developed for empirical economic research.
They are not "end-goals" or outputs, but instruments that I have built for myself and my colleagues to have a better overview of the data. 

---

### Structural Breaks in HS6 code

The goal of the research project is to analyse what happens to incumbents of old technologies. To better identify this "old technologies" and have a better overview of the large dataset we are using, I built this dashboards to look at the trends in the value of trade all HS6 goods available in the BACI data. One can text search for any good. Furthermore, I replicated the IGPC Indicator (Fezter et alii 2024) that takes into consideration not only value of trade of good i, but also all values of connected goods. Lastly, we used the conversion table from PATSTAT to connect HS6 goods to IPC classes to learn more about the levels of innovation within that sector. 

**App:** [Shiny Link](https://matciani.shinyapps.io/structural_breaks/#section-trade-data)  
**Code:** `Structural Breaks in HS6 goods.Rmd`


#### Sources:
Trade data: [BACI CEPII](https://www.cepii.fr/CEPII/en/bdd_modele/bdd_modele_item.asp?id=37)

Integrated Global Product Centrality: [AI-Generated Production Network](https://aipnet.io/paper/) 

Patent Data: [PATSTAT](https://www.epo.org/en/searching-for-patents/business/patstat) 

---

### Geography of Conflicts

We built this dashboard to visualise conflicts distributed in time and geographically. The events are colour-coded based on the type of conflict (state-based, non-state, and one-sided) and proportional in size to the severity of the event in terms of the number of deaths. The UCDP already has a public dashboard, but we were interested in recreating it to be able to make it better fit our research needs. 


**App:** [Shiny Link](https://matciani.shinyapps.io/Conflicts/)
**Code:** `Geography of Conflicts.R`

#### Source: 
Conflict data: [UCDP Georeferenced Event Dataset (GED)](https://ucdp.uu.se/)
