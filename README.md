This is a .py file with CS estimates based on the WHO CS estimation tool/methodology. 

Congenital Syphilis (CS) modelling equations:
Number of syphilis infected pregnancies = Number of pregnancies X maternal prevalence 
Percentage of pregnancies treated = ANC coverage X screening coverage X treatment coverage   
(assumption: women who don’t attend ANC or who attend ANC but are not screened are not treated) 
 
Number of untreated syphilis infected pregnancies = Number of syphilis infected pregnancies X (100 – percentage of pregnancies treated)/100 
Number of CS cases in untreated syphilis infected pregnancies = Number of untreated syphilis infected pregnancies  
Number of ABOs in untreated syphilis infected pregnancies = ABO Risk (currently 0.52) X Number of untreated syphilis infected pregnancies 
 
Total number of ABOs in untreated syphilis infected pregnancies :
•	Total liveborns with “clinical” CS in untreated women = CS risk liveborn (currently 0.16) X  Number untreated syphilis infected pregnancies 
•	Total  stillborns from CS in untreated women = CS risk stillborn (currently 0.21) X  Number untreated syphilis infected pregnancies 
•	Total neonatal deaths from CS in untreated women  = CS risk neonatal death (currently 0.09) X  Number untreated syphilis infected pregnancies 
•	Total premature/ LBW from CS in untreated women  = CS risk prematurity or LBW (currently 0.06) X  Number untreated syphilis infected pregnancies 

