1. Input: NA, Output: OrderRetrieveRQ/@Version, Remarks: Hardcoded as 17.2
2. Input: AMA_ConnectivityLayerRQ/Requests/Request/Context/correlationID, Output: OrderRetrieveRQ/@TransactionIdentifier
3. Input: AMA_ConnectivityLayerRQ/Requests/Request/Context/correlationID, Output: OrderRetrieveRQ/@CorrelationID
4. Input: NA, Output: OrderRetrieveRQ/PointOfSale/Location/CountryCode, Remarks: Hardcoded as FR
5. Input: NA, Output: OrderRetrieveRQ/PointOfSale/Location/CityCode, Remarks: Hardcoded as NCE
6. Input: NA, Output: OrderRetrieveRQ/Document/@id, Remarks: Hardcoded as document
7. Input: AMA_ConnectivityLayerRQ/Requests/Request/TravelAgency, Output: OrderRetrieveRQ/Party/Sender/TravelAgencySender
8. Input: AMA_ConnectivityLayerRQ/Requests/Request/TravelAgency/Name, Output: OrderRetrieveRQ/Party/Sender/TravelAgencySender/Name
9. Input: NA, Output: OrderRetrieveRQ/Party/Sender/TravelAgencySender/PseudoCity, Remarks: Hardcoded as
AH9D  
10. Input: AMA_ConnectivityLayerRQ/Requests/Request/TravelAgency/IATA_Number, Output: OrderRetrieveRQ/Party/Sender/TravelAgencySender/IATA_Number
11. Input: AMA_ConnectivityLayerRQ/Requests/Request/TravelAgency/IATA_Number, Output: OrderRetrieveRQ/Party/Sender/TravelAgencySender/AgencyID
12. Input: NA, Output: OrderRetrieveRQ/Party/Sender/TravelAgencySender/AgentUser/AgentUserID, Remarks: Hardcoded as xmluser001
13. Input: AMA_ConnectivityLayerRQ/Requests/Request/bookingSourceInfo/rloc, Output: OrderRetrieveRQ/Query/Filters/OrderID
14. Input: AMA_ConnectivityLayerRQ/Requests/Request/Context/Retailer/code, Output: OrderRetrieveRQ/Query/Filters/OrderID/@Owner