# Portfolio

This repository contains examples of Shiny dashboards I developed for empirical economic research and a web-based automation tool.
They are not "end-goals" or outputs, but instruments that I have built for myself and my colleagues to have a better overview of the data. 


---

### Structural Breaks in HS6 code

This dashboard supports research on the evolution of technologies in international trade. It visualizes trends in HS6 product-level trade data from BACI and helps identify technologies in decline.

Key features:
* Search and visualize trade values for any HS6 product  
* Reproduce the IGPC indicator (Fetzer et al., 2024) to show network-weighted product importance  
* Connect HS6 categories with patent IPC classes using the PATSTAT concordance

**App:** [Shiny Link](https://matciani.shinyapps.io/structural_breaks/#section-trade-data)  
**Code:** `Structural Breaks in HS6 goods.Rmd`


#### Sources:
Trade data: [BACI CEPII](https://www.cepii.fr/CEPII/en/bdd_modele/bdd_modele_item.asp?id=37)  
Integrated Global Product Centrality: [AI-Generated Production Network](https://aipnet.io/paper/)  
Patent Data: [PATSTAT](https://www.epo.org/en/searching-for-patents/business/patstat) 

---

### Geography of Conflicts

This dashboard maps and visualizes conflict events over time using UCDP GED data. It allows users to explore the temporal and geographic distribution of violent events.

Key features:
* Map conflicts by type (state-based, non-state, one-sided)  
* Bubble size proportional to event severity (fatalities)  
* Interactive filters to explore conflict dynamics across time and space

**App:** [Shiny Link](https://matciani.shinyapps.io/Conflicts/)  
**Code:** `Geography of Conflicts.R`

#### Source: 
Conflict data: [UCDP Georeferenced Event Dataset (GED)](https://ucdp.uu.se/)  


--- 

## Web Scraper

This tool automates the extraction of firm-level information from the Orbis database environment to support empirical research. It was designed to streamline data collection workflows and free time for analysis.

Key features:
* Logs in securely and retrieves a list of firms
* Searches each firm in the database interface and downloads thier associated patent portfolios

**Code:** `Patent Data from Firm Profile.py`

