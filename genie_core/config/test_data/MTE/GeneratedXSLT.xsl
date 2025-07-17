<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
           xmlns:ns0="http://www.amadeus.net" exclude-result-prefixes="ns0">
    <xsl:output method="xml" indent="yes"/>

    <!-- Template section -->
    <xsl:template match="/">
        <root>
            <!-- 1) product_id -->
            <product_id>7910e870-01d6-49e3-988c-698c8c388824</product_id>

            <!-- 2) coverage_start_date -->
            <coverage_start_date>
                <xsl:value-of select="concat(
                    substring(/ns0:InsuranceSmartShoppingRequest/ns0:insurancePlanSection/ns0:itineraryInfo/ns0:segmentDetails/ns0:flightDate/ns0:departureDate, 1, 4),
                    '-',
                    substring(/ns0:InsuranceSmartShoppingRequest/ns0:insurancePlanSection/ns0:itineraryInfo/ns0:segmentDetails/ns0:flightDate/ns0:departureDate, 5, 2),
                    '-',
                    substring(/ns0:InsuranceSmartShoppingRequest/ns0:insurancePlanSection/ns0:itineraryInfo/ns0:segmentDetails/ns0:flightDate/ns0:departureDate, 7, 2)
                )"/>
            </coverage_start_date>

            <!-- 3) coverage_end_date -->
            <coverage_end_date>
                <xsl:value-of select="concat(
                    substring(/ns0:InsuranceSmartShoppingRequest/ns0:insurancePlanSection/ns0:itineraryInfo/ns0:segmentDetails/ns0:flightDate/ns0:arrivalDate, 1, 4),
                    '-',
                    substring(/ns0:InsuranceSmartShoppingRequest/ns0:insurancePlanSection/ns0:itineraryInfo/ns0:segmentDetails/ns0:flightDate/ns0:arrivalDate, 5, 2),
                    '-',
                    substring(/ns0:InsuranceSmartShoppingRequest/ns0:insurancePlanSection/ns0:itineraryInfo/ns0:segmentDetails/ns0:flightDate/ns0:arrivalDate, 7, 2)
                )"/>
            </coverage_end_date>

            <!-- 4) coverage_start_hour_number -->
            <coverage_start_hour_number>
                <xsl:value-of select="substring(/ns0:InsuranceSmartShoppingRequest/ns0:insurancePlanSection/ns0:itineraryInfo/ns0:segmentDetails/ns0:flightDate/ns0:departureTime, 1, 2)"/>
            </coverage_start_hour_number>

            <!-- 5) coverage_end_hour_number -->
            <coverage_end_hour_number>
                <xsl:value-of select="substring(/ns0:InsuranceSmartShoppingRequest/ns0:insurancePlanSection/ns0:itineraryInfo/ns0:segmentDetails/ns0:flightDate/ns0:arrivalTime, 1, 2)"/>
            </coverage_end_hour_number>

            <!-- 6) currency -->
            <currency>
                <xsl:choose>
                    <xsl:when test="ns0:InsuranceSmartShoppingRequest/ns0:insuranceOptionSection/ns0:insuranceOptionDetails/ns0:pricingInformations/ns0:agentOverwritecurrencyelse">
                        <xsl:value-of select="ns0:InsuranceSmartShoppingRequest/ns0:insuranceOptionSection/ns0:insuranceOptionDetails/ns0:pricingInformations/ns0:agentOverwritecurrencyelse"/>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:value-of select="ns0:InsuranceSmartShoppingRequest/ns0:insuranceOptionSection/ns0:insuranceOptionDetails/ns0:pricingInformations/ns0:preferredCurrencyCode"/>
                    </xsl:otherwise>
                </xsl:choose>
            </currency>

            <!-- 7) exposure_name -->
            <exposure_name>
                <xsl:value-of select="ns0:InsuranceSmartShoppingRequest/ns0:subscriberAddressSection[ns0:nameDetails/ns0:nameInformation/ns0:qualifier = 'ADE']/ns0:nameDetails/ns0:nameInformation/ns0:name"/>
            </exposure_name>

            <!-- 8) exposure_total_coverage_amount -->
            <exposure_total_coverage_amount>
                <xsl:variable name="amount" select="ns0:InsuranceSmartShoppingRequest/ns0:insurancePlanSection/ns0:travelValue/ns0:monetaryDetails[1]/ns0:amount"/>
                <xsl:value-of select="number($amount) div 1000"/>
            </exposure_total_coverage_amount>

            <!-- 9) lang_locale -->
            <lang_locale>
                <xsl:variable name="lang">
                    <xsl:choose>
                        <xsl:when test="ns0:InsuranceSmartShoppingRequest/ns0:languageCode/ns0:userPreferences/ns0:codedLanguage">
                            <xsl:value-of select="ns0:InsuranceSmartShoppingRequest/ns0:languageCode/ns0:userPreferences/ns0:codedLanguage"/>
                        </xsl:when>
                        <xsl:otherwise>
                            <xsl:value-of select="ns0:InsuranceSmartShoppingRequest/ns0:originatorSection/ns0:originatorDetails/@language"/>
                        </xsl:otherwise>
                    </xsl:choose>
                </xsl:variable>
                <xsl:choose>
                    <xsl:when test="$lang = 'EN'">
                        <xsl:text>EN-US</xsl:text>
                    </xsl:when>
                    <xsl:when test="$lang = 'FR'">
                        <xsl:text>FR-FR</xsl:text>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:value-of select="$lang"/>
                    </xsl:otherwise>
                </xsl:choose>
            </lang_locale>

            <!-- 10) external_id -->
            <external_id>
                <xsl:text>R12A34RG</xsl:text>
            </external_id>

            <!-- 11) billing_address -->
            <billing_address>
                <address_line_1>
                    <xsl:value-of select="//ns0:subscriberAddressSection[ns0:nameDetails/ns0:nameInformation/ns0:qualifier='ARE']/ns0:addressInfo/ns0:addressDetails/ns0:line1[1]"/>
                </address_line_1>
                <address_line_2>
                    <xsl:value-of select="//ns0:subscriberAddressSection[ns0:nameDetails/ns0:nameInformation/ns0:qualifier='ARE']/ns0:addressInfo/ns0:addressDetails/ns0:line1[2]"/>
                </address_line_2>
                <city>
                    <xsl:value-of select="//ns0:subscriberAddressSection[ns0:nameDetails/ns0:nameInformation/ns0:qualifier='ARE']/ns0:addressInfo/ns0:city"/>
                </city>
                <region>
                    <xsl:choose>
                        <xsl:when test="ns0:InsuranceSmartShoppingRequest/ns0:subscriberAddressSection[ns0:nameDetails/ns0:nameInformation/ns0:qualifier='ARE']/ns0:addressInfo/ns0:regionDetails[ns0:qualifier='84']">
                            <xsl:value-of select="ns0:InsuranceSmartShoppingRequest/ns0:subscriberAddressSection[ns0:nameDetails/ns0:nameInformation/ns0:qualifier='ARE']/ns0:addressInfo/ns0:regionDetails[ns0:qualifier='84']/ns0:name"/>
                        </xsl:when>
                        <xsl:when test="ns0:InsuranceSmartShoppingRequest/ns0:subscriberAddressSection[ns0:nameDetails/ns0:nameInformation/ns0:qualifier='ARE']/ns0:addressInfo/ns0:locationDetails[ns0:qualifier='84']">
                            <xsl:value-of select="ns0:InsuranceSmartShoppingRequest/ns0:subscriberAddressSection[ns0:nameDetails/ns0:nameInformation/ns0:qualifier='ARE']/ns0:addressInfo/ns0:locationDetails[ns0:qualifier='84']/ns0:name"/>
                        </xsl:when>
                    </xsl:choose>
                </region>
                <country>
                    <xsl:choose>
                        <xsl:when test="ns0:InsuranceSmartShoppingRequest/ns0:subscriberAddressSection[ns0:nameDetails/ns0:nameInformation/ns0:qualifier='ARE']/ns0:addressInfo/ns0:locationDetails[ns0:qualifier='162']">
                            <xsl:value-of select="ns0:InsuranceSmartShoppingRequest/ns0:subscriberAddressSection[ns0:nameDetails/ns0:nameInformation/ns0:qualifier='ARE']/ns0:addressInfo/ns0:locationDetails[ns0:qualifier='162']/ns0:name"/>
                        </xsl:when>
                        <xsl:when test="ns0:InsuranceSmartShoppingRequest/ns0:subscriberAddressSection[ns0:nameDetails/ns0:nameInformation/ns0:qualifier='ARE']/ns0:addressInfo/ns0:regionDetails[ns0:qualifier='162']">
                            <xsl:value-of select="ns0:InsuranceSmartShoppingRequest/ns0:subscriberAddressSection[ns0:nameDetails/ns0:nameInformation/ns0:qualifier='ARE']/ns0:addressInfo/ns0:regionDetails[ns0:qualifier='162']/ns0:name"/>
                        </xsl:when>
                    </xsl:choose>
                </country>
                <postal_code>
                    <xsl:variable name="zipFromARE" select="/ns0:InsuranceSmartShoppingRequest/ns0:subscriberAddressSection[ns0:nameDetails/ns0:nameInformation/ns0:qualifier='ARE']/ns0:addressInfo/ns0:zipCode"/>
                    <xsl:choose>
                        <xsl:when test="$zipFromARE and string($zipFromARE) != ''">
                            <xsl:value-of select="$zipFromARE"/>
                        </xsl:when>
                        <xsl:otherwise>
                            <xsl:value-of select="/ns0:InsuranceSmartShoppingRequest/ns0:subscriberAddressSection[ns0:addressInfo/ns0:zipCode][1]/ns0:addressInfo/ns0:zipCode"/>
                        </xsl:otherwise>
                    </xsl:choose>
                </postal_code>
            </billing_address>
        </root>
    </xsl:template>
</xsl:stylesheet>