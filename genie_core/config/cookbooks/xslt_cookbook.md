{
  "key": "MAP_ONLY_DIGITS",
  "code": "translate(., concat(' `~!@#$%^&amp;*()-_=+[]{}|\\:;&quot;',&quot;',./&lt;&gt;?abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ&quot;), '')",
  "example": "<xsl:value-of select=\"translate(Request/TravelAgency/Contact/Phone/PhoneNumber, concat(' `~!@#$%^&amp;*()-_=+[]{}|\\:;&quot;',&quot;',./&lt;&gt;?abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ&quot;), '')\"/>"
},
{
"key": "LEFT_TRIM_AND_EXTRACT_DIGITS",
"description": "Extract the digits from the node, use the number function to convert the result of the substring function, which extracts from the left all the digits till it reaches a non numeric char",
"code": "number(substring(., 1, (string-length(string(.)) - 1)))"
},
{
  "key": "GET_LAST_CHARACTER",
  "code":"substring(., string-length(string(.)), 1)"
},
{
"key": "MAP_INPUT_TO_OUTPUT",  
"description": "Map Input value to the corresponding output value, for all other values map as is",
"example": "<xsl:choose>\n<xsl:when test=\"$input='Input1'\">\n<xsl:value-of select=\"'Output1'\"/>\n</xsl:when>\n<xsl:when test=\"$input='Input2'\">\n<xsl:value-of select=\"'Output2'\"/>\n</xsl:when>\n<xsl:otherwise>\n<xsl:value-of select=\"Input\"/>\n</xsl:otherwise>\n</xsl:choose>"
}
