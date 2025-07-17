**AMA_ConnectivityLayerRQ**| **OrderRetrieveRQ**| **Remarks**| **Type**  
1. **Input:** AMA_ConnectivityLayerRQ/Requests/Request/Context/correlationID  
    **Output:** OrderRetrieveRQ/@TransactionIdentifier  
    **Type:** Attribute  

2. **Input:** AMA_ConnectivityLayerRQ/Requests/Request/Context/correlationID  
    **Output:** OrderRetrieveRQ/@CorrelationID  
    **Type:** Attribute  

3. **Output:** OrderRetrieveRQ/@Version  
    **Remarks:** Hardcoded as 17.2  
    **Type:** Attribute  

4. **Output:** OrderRetrieveRQ/PointOfSale/Location/CountryCode  
    **Remarks:** Hardcoded as FR  

5. **Output:** OrderRetrieveRQ/PointOfSale/Location/CityCode  
    **Remarks:** Hardcoded as NCE  

6. **Output:** OrderRetrieveRQ/Document/@id  
    **Remarks:** Hardcoded as document  
    **Type:** Attribute  

7. **Input:** AMA_ConnectivityLayerRQ/Requests/Request/TravelAgency  
    **Output:** OrderRetrieveRQ/Party/Sender/TravelAgencySender  
    **Remarks:** Optional  

8. **Input:** AMA_ConnectivityLayerRQ/Requests/Request/TravelAgency/Name  
    **Output:** OrderRetrieveRQ/Party/Sender/TravelAgencySender/Name  

9. **Output:** OrderRetrieveRQ/Party/Sender/TravelAgencySender/PseudoCity  
    **Remarks:** Hardcoded as AH9D  

10. **Input:** AMA_ConnectivityLayerRQ/Requests/Request/TravelAgency/IATA_Number  
     **Output:** OrderRetrieveRQ/Party/Sender/TravelAgencySender/IATA_Number  

11. **Input:** AMA_ConnectivityLayerRQ/Requests/Request/TravelAgency/IATA_Number  
     **Output:** OrderRetrieveRQ/Party/Sender/TravelAgencySender/AgencyID  

12. **Output:** OrderRetrieveRQ/Party/Sender/TravelAgencySender/AgentUser/AgentUserID  
     **Remarks:** Hardcoded as xmluser001  

13. **Input:** AMA_ConnectivityLayerRQ/Requests/Request/bookingSourceInfo/rloc  
     **Output:** OrderRetrieveRQ/Query/Filters/OrderID  

14. **Input:** AMA_ConnectivityLayerRQ/Requests/Request/Context/Retailer/code  
     **Output:** OrderRetrieveRQ/Query/Filters/OrderID/@Owner  
     **Type:** Attribute  
