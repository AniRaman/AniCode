1. Input: NA, Output: OrderCreateRQ/@Version, Remarks: Hardcoded as 17.2
2. Input: Request/Context/correlationID, Output: OrderCreateRQ/@CorrelationID, Remarks: Optional
2. Input: Request/Context/correlationID, Output: OrderCreateRQ/@TransactionIdentifier, Remarks: Optional
3. Input: NA, Output: OrderCreateRQ/PointOfSale/Location/CountryCode, Remarks: Hardcoded as FR
4. Input: NA, Output: OrderCreateRQ/PointOfSale/Location/CityCode, Remarks: Hardcoded as NCE
5. Input: NA, Output: OrderCreateRQ/Document/@id, Remarks: Hardcoded as document
6. Input: NA, Output: OrderCreateRQ/Party/Sender/TravelAgencySender/PseudoCity, Remarks: Hardcoded as AH9D
7. Input: Request/TravelAgency, Output: OrderCreateRQ/Party/Sender/TravelAgencySender
8. Input: Request/TravelAgency/IATA_Number, Output: OrderCreateRQ/Party/Sender/TravelAgencySender/IATA_Number
9. Input: Request/TravelAgency/IATA_Number, Output: OrderCreateRQ/Party/Sender/TravelAgencySender/AgencyID
10. Input: Request/TravelAgency/Name, Output: OrderCreateRQ/Party/Sender/TravelAgencySender/Name
11. Input: Request/TravelAgency/Contact/Email/EmailAddress, Output: Party/Sender/TravelAgencySender/Contacts/Contact/EmailContact/Address
12. Input: Request/TravelAgency/Contact/Phone/PhoneNumber, Output: OrderCreateRQ/Party/Sender/TravelAgencySender/Contacts/Contact/PhoneContact/Number
13. Input: Request/TravelAgency/Contact/Address/line, Output: Party/Sender/TravelAgencySender/Contacts/Contact/AddressContact/Street
14. Input: Request/TravelAgency/Contact/Address/line, Output: Party/Sender/TravelAgencySender/Contacts/Contact/AddressContact/Street
15. Input: Request/TravelAgency/Contact/Address/CityName, Output: Party/Sender/TravelAgencySender/Contacts/Contact/AddressContact/CityName
16. Input: Request/TravelAgency/Contact/Address/Zip, Output: Party/Sender/TravelAgencySender/Contacts/Contact/AddressContact/PostalCode
17. Input: Request/TravelAgency/Contact/Address/CountryCode, Output: Party/Sender/TravelAgencySender/Contacts/Contact/AddressContact/CountryCode
18. Input: NA, Output: OrderCancelRQ/Party/Sender/TravelAgencySender/AgentUser/AgentUserID, Remarks: Hardcoded as xmluser001