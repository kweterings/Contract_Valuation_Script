# Contract Valuation Program: Client/Trader Agreement
###### Made by Kai Weterings, 16/11/2023

I present to you an example/prototype run at a contract valuation program. This type of script could be a potential
basis for a fully automated quoting to clients. This program is based on data for the market for 
natural gas, where a pricing model is used to predict the prices at given dates of client actions. Client actions being
either injections or withdrawals of a given volume of natural gas into or out of a natural gas storage facility
(injection occurring at client purchase and withdrawal occurring at client sell). 

The valuation of a contract is simple: the difference between the price you can sell and the price you are able to buy.
This program runs on a previously made pricing model to determine this difference (of course this model can be changed
if the parameters of a given contract will change).  
However, there will also be extra costs incurred to the client during the duration of the contract. There is will rental/
usage costs for the storage facility, logistical costs, etc...  
Hence, various measures to automate the total effective contract/agreement valuation in the code have been taken to make
sure all cash flows are being taken into account.

In addition, there are other parameters which affect the behaviour of the contract which need to be taken into account.
Such as the ability for the client to choose multiple dates to inject or withdraw a set volume of natural gas. Therefore,
the program allows as many dates as the client wants to do so, making sure all parameters to the contract are not violated
in the process.  
Other simple constrictions, such as maximum storage capacities have been implemented.
Also, this code takes into account a daily limit for injection or withdrawal, in and out, of the storage facility.
In this specific case, the injection and withdrawal were assumed to be separate, with their own daily limits, i.e. an
injection will not interfere with a withdrawal. This means that some client actions will need to be delayed as others 
done previously may not yet be complete. These intricacies, whether it is backlogged volumes to be injected or possible 
periods of surpassed maximum storage capacity between client action dates, have all been accounted for in the code.

Note to user: Please be aware that this is not a pricing model/contract valuation script used by any official traders
and/or trading companies. This is simply a project fueled by my own intrigue in the subject and desire to understand the
methods behind quantitative research.

Thank you for taking the time to look through my code. Of course, if you have any questions do not hesitate to send me a 
message on any of my listed contacts.