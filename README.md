# SH06 Main


## Project overview
SH06 is working with PEAK to develop a protien structure storage application that queries three external databases; AlphaFold, UniProt and EBI to serve protien structure files. 

Real protien structures will be selected from UniProt which will then be used to extract data from the protien data bank (EBI).
Already predicted structures will be gathered from AlphaFold using a weighting algorithm to select the 'best' prediction.

If a query for a protien structure is unsuccesful because it is not found in a known database, a request to predict the protien structure should be sent to AlphaFold2. These predictions are resource intensive so distributing tasks to multiple workers should be done where possible. It is also important to avoid queueing a request for a protien prediction that is in the process of being requested

All workloads of the application must run as containers, originally in Docker however this is expected to be expanded into a kubernetes cluster in the future.


## useful info - commands
## how to guide
## file structure
