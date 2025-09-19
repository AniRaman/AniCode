1. Input: Product ID, Remarks: product_id
2. Input: Coverage start date, Output: /InsuranceSmartShoppingRequest/insurancePlanSection/itineraryInfo/segmentDetails/flightDate/departureDate, Remarks: coverage_start_date
3. Input: Coverage end date, Output: /InsuranceSmartShoppingRequest/insurancePlanSection/itineraryInfo/segmentDetails/flightDate/arrivalDate, Remarks: coverage_end_date
4. Input: Coverage start hour (24 hr format), Output: /InsuranceSmartShoppingRequest/insurancePlanSection/itineraryInfo/segmentDetails/flightDate/departureTime
5. Input: coverage_start_hour_number, Output: S, Remarks: O
of the covered days - overrides the Product default if provided. Required if
the Product has no default. **Should be provided in the local time of the
location of the guarantee.** Build only the hour number  
6. Input: Coverage end hour (24 hr format), Output: /InsuranceSmartShoppingRequest/insurancePlanSection/itineraryInfo/segmentDetails/flightDate/arrivalTime
7. Input: coverage_end_hour_number, Output: S, Remarks: M
the covered days - overrides the Product default if provided. Required if the
Product has no default. Should be provided in the local time of the location
of the guarantee.Build only the hour number  
8. Input: Currency, Output: /InsuranceSmartShoppingRequest/insuranceOptionSection/insuranceOptionDetails/pricingInformations/agentOverwritecurrencyelse /InsuranceSmartShoppingRequest/insuranceOptionSection/insuranceOptionDetails/pricingInformations/preferredCurrencyCode, Remarks: currency
9. Input: Exposure name, Output: subscriberAddressSection with <qualifier>ADE</qualifier> will be taken into consideration and <name> element will be used for this exposure_name, Remarks: exposure_name
10. Input: Exposure latitude, Remarks: exposure_latitude
11. Input: Exposure longitude, Remarks: exposure_longitude
12. Input: Total coverage amount, Output: /InsuranceSmartShoppingRequest/insurancePlanSection/travelValue/monetaryDetails/amount, Remarks: exposure_total_coverage_amount
Language (Local)| Pick the language from
InsuranceSmartShoppingRequest/languageCode/userPreferences/codedLanguageif
13. Input: present, else/originatorSection/originatorDetails/@language, Output: lang_locale, Remarks: C
languages would be added in 2024 User preferred language can be sent  
14. Input: External ID, Remarks: external_id
15. Input: Billing Address, Output: /subscriberAddressSection[1]/nameDetails/qualifier="ARE"/name
16. Input: Address Line 1, Output: subscriberAddressSection/addressInfo/addressDetails/line1, Remarks: billing_address.address_line_1
17. Input: Address Line 2, Output: subscriberAddressSection/addressInfo/addressDetails/line2, Remarks: billing_address.address_line_2
18. Input: City, Output: /addressInfo/city, Remarks: billing_address.city
19. Input: Region, Output: Check for /addressInfo/regionDetails/qualifier = 84If found, pick up the state from /addressInfo/regionDetails/name If not found, check if /addressInfo/locationDetails/qualifier = 84If yes, pick up the state from /addressInfo/locationDetails/name, Remarks: billing_address.region
20. Input: country, Output: Check for /addressInfo/locationDetails/qualifier = 162If found, pick up the country from /addressInfo/locationDetails/nameIf not found, chec if /addressInfo/regionDetails/qualifier = 162If yes /addressInfo/regionDetails/name, Remarks: billing_address.country
21. Input: postal code, Output: /addressInfo/zipCode, Remarks: billing_address.postal_code