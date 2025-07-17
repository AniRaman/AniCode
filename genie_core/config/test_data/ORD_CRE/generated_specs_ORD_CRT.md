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
19. Input: Request/set, Output: OrderCreateRQ/Query/Order/Offer
20. Input: Request/set/ID, Output: OrderCreateRQ/Query/Order/Offer/@OfferID
21. Input: Request/set/property/Value, Output: OrderCreateRQ/Query/Order/Offer/@Owner, Remarks: Key = OwnerCode, Value is mapped to OwnerCode
22. Input: Request/set/TID, Output: OrderCreateRQ/Query/Order/Offer/@ResponseID
23. Input: Request/set/Product/ID, Output: OrderCreateRQ/Query/Order/Offer/OfferItem/@OfferItemID
24. Input: Request/set/Product/RefIDs, Output: OrderCreateRQ/Query/Order/Offer/OfferItem/PassengerRefs
25. Input: Request/set/product/EST/Data/seatNbr, Output: OrderCreateRQ/Query/Order/Offer/OfferItem/SeatSelection/Row, Remarks: Last element is column and before that is row
26. Input: Request/set/product/EST/Data/seatNbr, Output: OrderCreateRQ/Query/Order/Offer/OfferItem/SeatSelection/Column
27. Input: N/A, Output: Query/Payments/Payment/Method/Cash/@CashInd, Remarks: Hardcoded as "true"
28. Input: N/A, Output: Query/Payments/Payment/Amount, Remarks: Hardcoded as "0.00"
29. Input: Request/actor/ID, Output: OrderCreateRQ/Query/DataLists/PassengerList/Passenger/@PassengerID
30. Input: Request/actor/PTC, Output: OrderCreateRQ/Query/DataLists/PassengerList/Passenger/PTC, Remarks: PTC supported by different NDC provider is to be supported. Please refer PTC Conversion
31. Input: Request/address/CountryCode, Output: OrderCreateRQ/Query/DataLists/PassengerList/Passenger/ResidenceCountryCode, Remarks: As per Farelogix response, Residence country code is neither validated or returned in the response. Hence the encoding is removed on our side
32. Input: Request/actor/nationality/code, Output: OrderCreateRQ/Query/DataLists/PassengerList/Passenger/CitizenshipCountryCode
33. Input: N/A, Output: OrderCreateRQ/Query/DataLists/PassengerList/Individual
34. Input: Request/actor/DateOfBirth, Output: OrderCreateRQ/Query/DataLists/PassengerList/Passenger/Individual/Birthdate
35. Input: Requests/Request/actor/Name/Type, Output: OrderCreateRQ/Query/DataLists/PassengerList/Passenger/Individual/Gender, Remarks: (Type is other then Gender is Unspecified and both rest it is direct mapping)
36. Input: Request/actor/Name/Title, Output: OrderCreateRQ/Query/DataLists/PassengerList/Passenger/Individual/NameTitle
37. Input: Request/actor/Name/FirstName, Output: OrderCreateRQ/Query/DataLists/PassengerList/Passenger/Individual/GivenName
38. Input: Request/actor/Name/LastName, Output: OrderCreateRQ/Query/DataLists/PassengerList/Passenger/Individual/Surname
39. Input: Request/actor/loyalty/companyCode, Output: OrderCreateRQ/Query/DataLists/PassengerList/Passenger/LoyaltyProgramAccount/Airline/AirlineDesignator
40. Input: Request/actor/loyalty/identifier, Output: OrderCreateRQ/Query/DataLists/PassengerList/Passenger/LoyaltyProgramAccount/AccountNumber
41. Input: Request/actor/docRef, Output: OrderCreateRQ/Query/DataLists/PassengerList/Passenger/IdentityDocument, Remarks: CREATE_DOC_REF_NODE Optional
42. Input: Request/actor/docRef, Output: OrderCreateRQ/Query/DataLists/PassengerList/Passenger/IdentityDocument, Remarks: CREATE_DOC_REF_NODE TYPE1_DocRef_IDENTIFIER TaxIdentifier does not exist and Type exists
43. Input: Request/actor/docRef, Output: OrderCreateRQ/Query/DataLists/PassengerList/Passenger/IdentityDocument, Remarks: CREATE_DOC_REF_NODE TYPE2_DocRef_IDENTIFIER as
44. Input: Request/actor/docRef, Output: OrderCreateRQ/Query/DataLists/PassengerList/Passenger/IdentityDocument, Remarks: CREATE_DOC_REF_NODE TYPE3_DocRef_IDENTIFIER Redress Case:- Actor/redress exist
45. Input: Request/actor/docRef, Output: OrderCreateRQ/Query/DataLists/PassengerList/Passenger/IdentityDocument, Remarks: CREATE_DOC_REF_NODE TYPE4_DocRef_IDENTIFIER Target =UA or UAD and Visa type =R. Identity document number comes from Visa
46. Input: Request/actor/docRef, Output: OrderCreateRQ/Query/DataLists/PassengerList/Passenger/IdentityDocument, Remarks: CREATE_DOC_REF_NODE TYPE5_DocRef_IDENTIFIER Target =UA or UAD and Visa type =K
46. Input: Request/actor/docRef, Output: OrderCreateRQ/Query/DataLists/PassengerList/Passenger/IdentityDocument/IdentityDocumentNumber, Remarks: 
47. Input: Request/actor/docRef/type, Output: OrderCreateRQ/Query/DataLists/PassengerList/Passenger/IdentityDocument/IdentityDocumentType, Remarks: If Identity document type "P" in AMA_CLRQ, encode it as "PT" in OrderCreateRQ, as it requires for SSR DOCS creation in provider system.
43. Input: Request/actor/docRef, Output: OrderCreateRQ/Query/DataLists/PassengerList/Passenger/IdentityDocument/IdentityDocumentNumber
44. Input: Request/actor/docRef/issuer, Output: OrderCreateRQ/Query/DataLists/PassengerList/Passenger/IdentityDocument/IssuingCountryCode
45. Input: Request/actor/docRef/nationality, Output: OrderCreateRQ/Query/DataLists/PassengerList/Passenger/IdentityDocument/CitizenshipCountryCode
46. Input: Request/actor/docRef/issuanceDate, Output: OrderCreateRQ/Query/DataLists/PassengerList/Passenger/IdentityDocument/IssueDate
47. Input: Request/actor/docRef/expirationDate, Output: OrderCreateRQ/Query/DataLists/PassengerList/Passenger/IdentityDocument/ExpiryDate
48. Input: Request/actor/Name/Type, Output: OrderCreateRQ/Query/DataLists/PassengerList/Passenger/IdentityDocument/Gender, Remarks: Direct Mapping
49. Input: Request/actor/docRef/dateOfBirth, Output: OrderCreateRQ/Query/DataLists/PassengerList/Passenger/IdentityDocument/Birthdate
50. Input: Request/actor/docRef/Visa, Output: OrderCreateRQ/Query/DataLists/PassengerList/Passenger/IdentityDocument/Visa, Remarks: Target should be UA or UAD and Visa type != R or K
51. Input: Request/actor/docRef/Visa/VisaNumber, Output: OrderCreateRQ/Query/DataLists/PassengerList/Passenger/IdentityDocument/Visa/VisaNumber, Remarks: For UA
52. Input: Request/actor/docRef/Visa/VisaType, Output: OrderCreateRQ/Query/DataLists/PassengerList/Passenger/IdentityDocument/Visa/VisaType, Remarks: On 1A side, we support visa type as V (Multiple visa is not supported)
53. Input: Request/actor/docRef/Visa/VisaHostCountryCode, Output: OrderCreateRQ/Query/DataLists/PassengerList/Passenger/IdentityDocument/Visa/VisaHostCountryCode, Remarks: For UA
54. Input: Request/actor/docRef/Visa/EnterBeforeDate, Output: OrderCreateRQ/Query/DataLists/PassengerList/Passenger/IdentityDocument/Visa/EnterBeforeDate, Remarks: For UA
55. Input: Request/actor/docRef/Visa/DurationOfStay, Output: OrderCreateRQ/Query/DataLists/PassengerList/Passenger/IdentityDocument/Visa/DurationOfStay, Remarks: For UA
56. Input: Request/actor/docRef/Visa/NumberOfEntries, Output: OrderCreateRQ/Query/DataLists/PassengerList/Passenger/IdentityDocument/Visa/NumberOfEntries, Remarks: For UA
57. Input: NA, Output: OrderCreateRQ/Query/DataLists/PassengerList/ContactInfoRef, Remarks: ContactInfoRef(Contact type doesn't exist then concat CI position of contact and ID)
58. Input: NA, Output: Request/actor/IdentificationCode, Remarks: This field shall contain CONTACT Input: Request/actor/RefIDs, Output: OrderCreateRQ/Query/DataLists/PassengerList/Passenger/InfantRef
59. Input: NA, Output: OrderCreateRQ/Query/DataLists/ContactList/ContactInformation
60. Input: NA, Output: ContactInformation 1, Remarks: ContactInformation1 (Contact type =CTC)
61. Input: NA, Output: ContactInformation 2, Remarks: ContactInformation2(Contact Type does not exist )
62. Input: NA, Output: ContactInformation 3, Remarks: ContactInformation3(Address exist and contact doesn't exist )
63. Input: NA, Output: OrderCreateRQ/Query/DataLists/ContactList/ContactInformation/ContactID (attribute), Remarks: Encoded by Connectivity Layer (concatenate CI position of contact and ID)
64. Input: Request/actor/address, Output: OrderCreateRQ/Query/DataLists/ContactList/ContactInformation/PostalAddress, Remarks: Contact Type = CTC and Company Name doesn't exist and AddresseeName does not exist
65. Input: Request/actor/address/label, Output: OrderCreateRQ/Query/DataLists/ContactList/ContactInformation/PostalAddress/Label
66. Input: Request/actor/address/line, Output: OrderCreateRQ/Query/DataLists/ContactList/ContactInformation/PostalAddress/Street
67. Input: Request/actor/address/zip, Output: OrderCreateRQ/Query/DataLists/ContactList/ContactInformation/PostalAddress/PostalCode
68. Input: Request/actor/address/cityName, Output: OrderCreateRQ/Query/DataLists/ContactList/ContactInformation/PostalAddress/CityName
69. Input: Request/actor/address/stateName, Output: OrderCreateRQ/Query/DataLists/ContactList/ContactInformation/PostalAddress/CountrySubdivisionName
70. Input: Request/actor/address/countryCode, Output: OrderCreateRQ/Query/DataLists/ContactList/ContactInformation/PostalAddress/CountryCode
71. Input: Request/actor/contact/contactType, Output: OrderCreateRQ/Query/DataLists/ContactList/ContactInformation/ContactType, Remarks: For example: GST or CTC based on SSRs added on ROB side
72. Input: Request/actor/contact, Output: OrderCreateRQ/Query/DataLists/ContactList/ContactInformation/ContactProvided
73. Input: Request/actor/contact/phone/label, Output: OrderCreateRQ/Query/DataLists/ContactList/ContactInformation/Phone/Label, Remarks: LH: For SSR CTCM Label to be send as 'Operational' AA,QF,UA: Map 'mobile' as 'operational', direct mapping otherwise
74. Input: Request/actor/contact/email/label, Output: OrderCreateRQ/Query/DataLists/ContactList/ContactInformation/ContactProvided/EmailAddress/Label, Remarks: LH: For SSR CTCE Label to be send as 'Operational' AA,UA: Map 'email' as 'operational', direct mapping otherwise
75. Input: Request/actor/contact/email, Output: OrderCreateRQ/Query/DataLists/ContactList/ContactInformation/ContactProvided/EmailAddress/EmailAddressValue
76. Input: Request/actor/contact/phone, Output: OrderCreateRQ/Query/DataLists/ContactList/ContactInformation/Phone, Remarks: Remove any characters except number in this field (This filtering is only valid for FLX carriers)
77. Input: Request/actor/contact/phone/overseasCode, Output: OrderCreateRQ/Query/DataLists/ContactList/ContactInformation/Phone/CountryDialingCode
78. Input: Request/actor/contact/phone, Output: OrderCreateRQ/Query/DataLists/ContactList/ContactInformation/Phone/PhoneNumber
79. Input: Request/actor/contact/ContactRefusedInd, Output: OrderCreateRQ/Query/DataLists/ContactList/ContactInformation/ContactNotProvided, Remarks: If ContactRefusedInd is true then "Empty Node" SSR CTCR will be added on TP side when customer/passenger refuse to provide the any contact information. Since FLX does not support this functionality as of today, end to end validation will be on hold