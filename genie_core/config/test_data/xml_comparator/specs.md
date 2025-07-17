1. Input: NA, Output: RESAGG_ExtractProfilesDataRQ/Requests/Request/action, Remarks: hardcoded create
2. Input: IATA_OrderViewRS/Response/DataLists/PaxJourneyList/PaxJourney/PaxJourneyID, Output: RESAGG_ExtractProfilesDataRQ/Requests/Request/set/product/PaxJourneyID, Remarks: BothID should be equal PaxSegmentID & PaxSegmentRefID  
3. Input: IATA_OrderViewRS/Response/DataLists/DatedMarketingSegmentList/DatedMarketingSegment/CarrierDesigCode, Output: RESAGG_ExtractProfilesDataRQ/Requests/Request/set/product/EAI/Data/serviceProvider/code
4. Input: IATA_OrderViewRS/Response/DataLists/DatedMarketingSegmentList/DatedMarketingSegment/MarketingCarrierFlightNumberText, Output: RESAGG_ExtractProfilesDataRQ/Requests/Request/set/product/EAI/Data/identifier
5. Input: IATA_OrderViewRS/Response/DataLists/DatedOperatingSegmentList/DatedOperatingSegment/CarrierDesigCode, Output: RESAGG_ExtractProfilesDataRQ/Requests/Request/set/product/EAI/Data/partnerInfo/serviceProvider/code
6. Input: IATA_OrderViewRS/Response/DataLists/DatedOperatingSegmentList/DatedOperatingSegment/OperatingCarrierFlightNumberText, Output: RESAGG_ExtractProfilesDataRQ/Requests/Request/set/product/EAI/Data/partnerInfo/identifier
7. Input: RESAGG_ExtractProfilesDataRQ/Requests/Request/set/product/EAI/Data/bkgClass, Output: RESAGG_ExtractProfilesDataRQ/Requests/Request/set/product/EAI/Data/bkgClass
8. Input: IATA_OrderViewRS/Response/DataLists/DatedMarketingSegmentList/DatedMarketingSegment/Dep/AircraftScheduledDateTime, Output: RESAGG_ExtractProfilesDataRQ/Requests/Request/set/product/EAI/Data/start/dateTime
9. Input: IATA_OrderViewRS/Response/DataLists/DatedMarketingSegmentList/DatedMarketingSegment/Dep/IATA_LocationCode, Output: RESAGG_ExtractProfilesDataRQ/Requests/Request/set/product/EAI/Data/start/locationCode
IATA_OrderViewRS/Response/DataLists/DatedMarketingSegmentList/DatedMarketingSegment/Arrival/AircraftScheduledDateTime  
10. Input: NA, Output: RESAGG_ExtractProfilesDataRQ/Requests/Request/set/product/EAI/Data/end/dateTime
IATA_OrderViewRS/Response/DataLists/DatedMarketingSegmentList/DatedMarketingSegment/Arrival/IATA_LocationCode  
11. Input: NA, Output: RESAGG_ExtractProfilesDataRQ/Requests/Request/set/product/EAI/Data/end/locationCode
12. Input: NA, Output: RESAGG_ExtractProfilesDataRQ/Requests/Request/set/product/EAI/Data/NIP, Remarks: NIP
is total count of passengers excluding infants (PTCs for Infants : INF and
ITF) & PassengerType shouldn’t be INF  
Count the no. of passengers (each Passenger ID)  
13. Input: IATA_OrderViewRS/Response/DataLists/DatedOperatingLegList/DatedOperatingLeg/CarrierAircraftType/CarrierAircraftTypeCode, Output: RESAGG_ExtractProfilesDataRQ/Requests/Request/set/product/EAI/Data/vehicle/code
14. Input: IATA_OrderViewRS/Response/DataLists/DatedOperatingSegmentList/DatedOperatingSegment/Duration, Output: RESAGG_ExtractProfilesDataRQ/Requests/Request/set/product/EAI/Data/duration
15. Input: NA, Output: RESAGG_ExtractProfilesDataRQ/Requests/Request/set/ExternalContext, Remarks: Map
ExternalContext only if PaxRefID exists under OrderItem/FareDetail  
16. Input: IATA_OrderViewRS/Response/Order/OrderItem/Service/OrderServiceAssociation/PaxSegmentRef/PaxSegmentRefID, Output: RESAGG_ExtractProfilesDataRQ/Requests/Request/set/product/RefIDs, Remarks: Map only if
PaxSegmentRefID exists - Direct mapping  
17. Input: IATA_OrderViewRS/Response/Order/OrderItem/Service/OrderServiceAssociation/DatedOperatingLegRef/DatedOperatingLegRefID, Output: RESAGG_ExtractProfilesDataRQ/Requests/Request/set/product/RefIDs, Remarks: Map only if
DatedOperatingLegRefID exists and other conditions fetch
PaxSegmentRefID<DatedOperatingLegRefID>seg0484134592-leg0</DatedOperatingLegRefID>Check
if "-legX" exists, then remove it and map only the seg ID value. As per above
example, map only "seg0484134592". Refer link for more details : To handle
Seats and Service associated at Leg level.
<https://rndwww.nce.amadeus.net/confluence/pages/viewpage.action?pageId=3675042844>  
18. Input: IATA_OrderViewRS/Response/Order/OrderItem/Service/OrderServiceAssociation/ServiceDefinitionRef/ServiceDefinitionRefID, Output: RESAGG_ExtractProfilesDataRQ/Requests/Request/set/product/ESR/ID, Remarks: Note: ESR
node will be repeated for each Service ID even though ServiceDefinitionRef is
same. If multiple services, then create multiple ESR and follow below logic to
generate ESR.  
Map ESR nodes only if
  1. FareDetail doesn't exist
  2. SeatOnLeg doesn't exit
  3. ServiceDefinitionID+ServiceDefinitionRefID
  
  
IATA_OrderViewRS/Response/Order/OrderItem/FareDetail not present +
IATA_OrderViewRS/Response/Datalists/ServiceDefinitionList/ServiceDefinition/ServiceDefinitionID
should be equal to
IATA_OrderViewRS/Response/Order/OrderItem/Service/OrderServiceAssociation/ServiceDefinitionRef/ServiceDefinitionRefID
+
IATA_OrderViewRS/Response/Order/OrderItem/Service/OrderServiceAssociation/SeatOnLeg
not present  
19. Input: IATA_OrderViewRS/Response/DataLists/ServiceDefinitionList/ServiceDefinition/RFIC, Output: RESAGG_ExtractProfilesDataRQ/Requests/Request/set/product/ESR/Data/priceCategory/code
Map only if ServiceDefinitionID=ServiceDefinitionRefID  
<RFIC>G</RFIC>  
20. Input: IATA_OrderViewRS/Response/DataLists/ServiceDefinitionList/ServiceDefinition/RFISC, Output: RESAGG_ExtractProfilesDataRQ/Requests/Request/set/product/ESR/Data/priceCategory/subCode
Map only if ServiceDefinitionID=ServiceDefinitionRefID  
<RFISC>0L8</RFISC>  
21. Input: IATA_OrderViewRS/Response/DataLists/ServiceDefinitionList/ServiceDefinition/Desc/DescText, Output: RESAGG_ExtractProfilesDataRQ/Requests/Request/set/product/ESR/Data/productDescription/text
Map only if its not FSR & CSR <DescText>BG25</DescText>  
If we receive "FSR" , "CSR" , "Free" and "Chargeable" respectively, do not map
the entire <Desc> node  
22. Input: IATA_OrderViewRS/Response/DataLists/ServiceDefinitionList/ServiceDefinition/ServiceCode, Output: RESAGG_ExtractProfilesDataRQ/Requests/Request/set/product/ESR/Data/code, Remarks: Map
only if ServiceDefinitionID=ServiceDefinitionRefID  
<ServiceCode>VYOP</ServiceCode>  
  
23. Input: IATA_OrderViewRS/Response/DataLists/DatedMarketingSegmentList/DatedMarketingSegment/CarrierDesigCode, Output: RESAGG_ExtractProfilesDataRQ/Requests/Request/set/product/ESR/Data/serviceProvider/code
<CarrierDesigCode>VY</CarrierDesigCode>  
Based on other logics  
Check if
OrderViewRS/Response/Order/OrderItem/Service/OrderServiceAssociation/ServiceDefinitionRef/OrderFlightAssociations/PaxSegmentRef/PaxSegmentRefID
matches with
OrderViewRS/Response/DataLists/PaxSegmentList/PaxSegment/PaxSegmentID then
take DatedMarketingSegmentRefId from PaxSegment and it should match to
OrderViewRS/Response/DataLists/DatedMarketingSegmentList/DatedMarketingSegmentId  
24. Input: IATA_OrderViewRS/Response/DataLists/PaxList/Pax/Remark/RemarkText, Output: RESAGG_ExtractProfilesDataRQ/Requests/Request/actor/ID, Remarks: Either direct
sequencing or mapping from OVRS  
Encode with provider PAX ID  
25. Input: Ex: PAX2, PAX3, etc., Output: RESAGG_ExtractProfilesDataRQ/Requests/Request/actor/TID, Remarks: Compare GivenName & Surname (under Individual of OVRS) with FirstName &
LastName of new req in creation. Accordingly , encode the PAXID  
26. Input: IATA_OrderViewRS/Response/DataLists/PaxList/Pax/IdentityDoc/IssuingCountryCode, Output: RESAGG_ExtractProfilesDataRQ/Requests/Request/actor/docRef/issuer, Remarks: If 3 letter
country code is returned, convert it in 2 letter country code.  
27. Input: IATA_OrderViewRS/Response/DataLists/PaxList/Pax/IdentityDoc/CitizenshipCountryCode, Output: RESAGG_ExtractProfilesDataRQ/Requests/Request/actor/docRef/nationality, Remarks: If 3
letter country code is returned, convert it in 2 letter country code.  
28. Input: IATA_OrderViewRS/Response/DataLists/PaxList/Pax/IdentityDoc/IdentityDocTypeCode, Output: RESAGG_ExtractProfilesDataRQ/Requests/Request/actor/docRef/type, Remarks: Map 'PT' as
'P'  
Map 'VI' as 'V' (visa is not supported by VY ,NK and 6E for now)  
29. Input: IATA_OrderViewRS/Response/DataLists/PaxList/Pax/Individual/GenderCode, Output: RESAGG_ExtractProfilesDataRQ/Requests/Request/actor/type, Remarks: Map 'M' as 'Male'
Map 'F' as 'Female'  
30. Input: IATA_OrderViewRS/Response/DataLists/PaxList/Pax/PTC, Output: RESAGG_ExtractProfilesDataRQ/Requests/Request/actor/PTC, Remarks: PTC Conversion in cpp
layer (in json)  
IATA_OrderViewRS/Response/DataLists/PaxList/Pax/Individual/GivenName | RESAGG_ExtractProfilesDataRQ/Requests/Request/actor/Name/FirstName  
|  
31. Input: IATA_OrderViewRS/Response/DataLists/PaxList/Pax/Individual/Surname, Output: RESAGG_ExtractProfilesDataRQ/Requests/Request/actor/Name/LastName
  
We don't have a way to export this macro.