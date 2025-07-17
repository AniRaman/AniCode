1. Input: NA, Output: OrderCreateRQ/@Version, Remarks: Hardcoded as 17.2
2. Input: Request/Context/correlationid, Output: OrderCreateRQ/@Correlationid
3. Input: Request/Context/correlationID, Output: OrderRetrieveRQ/@TransactionIdentifier
4. Input: NA, Output: OrderRetrieveRQ/PointOfSale/Location/CountryCode, Remarks: Hardcoded as FR
5. Input: NA, Output: OrderRetrieveRQ/PointOfSale/Location/CityCode, Remarks: Hardcoded as NCE
6. Input: NA, Output: OrderRetrieveRQ/Document/@id, Remarks: Hardcoded as document
7. Input: NA, Output: OrderRetrieveRQ/Party/Sender/TravelAgencySender/PseudoCity, Remarks: Hardcoded as
AH9D|  
8. Input: Request/TravelAgency/IATA_Number, Output: OrderRetrieveRQ/Party/Sender/TravelAgencySender/IATA_Number
9. Input: Request/TravelAgency/IATA_Number, Output: OrderRetrieveRQ/Party/Sender/TravelAgencySender/AgencyID
10. Input: Request/TravelAgency/Name, Output: Party/Sender/TravelAgencySender/Name
11. Input: Request/TravelAgency/Contact/Email/EmailAddress, Output: Party/Sender/TravelAgencySender/Contacts/Contact/EmailContact/Address
12. Input: Request/TravelAgency/Contact/Phone, Output: OrderCreateRQ/Party/Sender/TravelAgencySender/Contacts/Contact/PhoneContact/Number
13. Input: Request/TravelAgency/Contact/Address/line, Output: Party/Sender/TravelAgencySender/Contacts/Contact/AddressContact/Street
14. Input: Request/TravelAgency/Contact/Address/line, Output: Party/Sender/TravelAgencySender/Contacts/Contact/AddressContact/Street
15. Input: Request/TravelAgency/Contact/Address/CityName, Output: Party/Sender/TravelAgencySender/Contacts/Contact/AddressContact/CityName
16. Input: Request/TravelAgency/Contact/Address/Zip, Output: Party/Sender/TravelAgencySender/Contacts/Contact/AddressContact/PostalCode
17. Input: Request/TravelAgency/Contact/Address/CountryCode, Output: Party/Sender/TravelAgencySender/Contacts/Contact/AddressContact/CountryCode
18. Input: Request/set, Output: OrderCreateRQ/Query/Order/Offer
19. Input: Request/set/ID, Output: OrderCreateRQ/Query/Order/Offer/@OfferID