ruled_text = '''<xsl:template xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:tbf="http://www.altova.com/MapForce/UDF/tbf" xmlns:ns0="http://www.opentravel.org/OTA/2003/05" xmlns:xs="http://www.w3.org/2001/XMLSchema" match="/">
	<xsl:for-each select="@Description">
		<xsl:attribute name="Description" namespace="">
			<xsl:value-of select="substring(., 0, 62)"/>
		</xsl:attribute>
	</xsl:for-each>
	<xsl:for-each select="@GuaranteedInd">
		<xsl:attribute name="GuaranteedInd" namespace="">
			<xsl:value-of select="boolean(translate(normalize-space(string(.)), ' 0false', ''))"/>
		</xsl:attribute>
	</xsl:for-each>
	<xsl:for-each select="@IncludedInRate">
		<xsl:attribute name="IncludedInRate" namespace="">
			<xsl:value-of select="boolean(translate(normalize-space(string(.)), ' 0false', ''))"/>
		</xsl:attribute>
	</xsl:for-each>
	<xsl:for-each select="@IncludedInEstTotalInd">
		<xsl:attribute name="IncludedInEstTotalInd" namespace="">
			<xsl:value-of select="boolean(translate(normalize-space(string(.)), ' 0false', ''))"/>
		</xsl:attribute>
	</xsl:for-each>
	<xsl:for-each select="@RateConvertInd">
		<xsl:attribute name="RateConvertInd" namespace="">
			<xsl:value-of select="boolean(translate(normalize-space(string(.)), ' 0false', ''))"/>
		</xsl:attribute>
	</xsl:for-each>
	<xsl:for-each select="@RequiredInd">
		<xsl:attribute name="RequiredInd" namespace="">
			<xsl:value-of select="boolean(translate(normalize-space(string(.)), ' 0false', ''))"/>
		</xsl:attribute>
	</xsl:for-each>
	<xsl:for-each select="ns0:TaxAmounts">
		<TaxAmounts>
			<xsl:for-each select="ns0:TaxAmount">
				<TaxAmount>
					<xsl:attribute name="Total" namespace="">
						<xsl:value-of select="number(@Total)"/>
					</xsl:attribute>
					<xsl:attribute name="CurrencyCode" namespace="">
						<xsl:value-of select="@CurrencyCode"/>
					</xsl:attribute>
					<xsl:for-each select="@TaxCode">
						<xsl:attribute name="TaxCode" namespace="">
							<xsl:value-of select="."/>
						</xsl:attribute>
					</xsl:for-each>
					<xsl:for-each select="@Percentage">
						<xsl:attribute name="Percentage" namespace="">
							<xsl:value-of select="number(.)"/>
						</xsl:attribute>
					</xsl:for-each>
					<xsl:for-each select="@Description">
						<xsl:attribute name="Description" namespace="">
							<xsl:value-of select="."/>
						</xsl:attribute>
					</xsl:for-each>
				</TaxAmount>
			</xsl:for-each>
		</TaxAmounts>
	</xsl:for-each>
	<xsl:for-each select="ns0:MinMax">
		<MinMax>
			<xsl:for-each select="@MaxCharge">
				<xsl:attribute name="MaxCharge" namespace="">
					<xsl:value-of select="number(.)"/>
				</xsl:attribute>
			</xsl:for-each>
			<xsl:for-each select="@MinCharge">
				<xsl:attribute name="MinCharge" namespace="">
					<xsl:value-of select="number(.)"/>
				</xsl:attribute>
			</xsl:for-each>
			<xsl:for-each select="@MaxChargeDays">
				<xsl:attribute name="MaxChargeDays" namespace="">
					<xsl:value-of select="number(.)"/>
				</xsl:attribute>
			</xsl:for-each>
		</MinMax>
	</xsl:for-each>
	<xsl:for-each select="ns0:Calculation">
		<Calculation>
			<xsl:for-each select="@UnitCharge">
				<xsl:attribute name="UnitCharge" namespace="">
					<xsl:value-of select="number(.)"/>
				</xsl:attribute>
			</xsl:for-each>
			<xsl:for-each select="@UnitName">
				<xsl:attribute name="UnitName" namespace="">
					<xsl:value-of select="."/>
				</xsl:attribute>
			</xsl:for-each>
		</xsl:template> ''' 

from dotenv import load_dotenv, find_dotenv
import os
from openai import AzureOpenAI
import httpx
httpx_client = httpx.Client(verify=False)

_ = load_dotenv(find_dotenv())
o3_mini_model_name = os.getenv("o3_mini_MODEL_DEPLOYMENT_NAME")

o3client = AzureOpenAI(
  azure_endpoint = os.getenv("o3_mini_AZURE_OPENAI_ENDPOINT"), 
  api_key=os.getenv("o3_mini_AZURE_OPENAI_KEY"),  
  api_version=os.getenv("o3_mini_AZURE_API_VERSION"),
  http_client=httpx_client
)

def get_chat_completion(input_messages, model_name=o3_mini_model_name):
    try:
        print(f"Model Used: {o3_mini_model_name}")
        response = o3client.chat.completions.create(
            model=model_name,
            messages=input_messages,
            stop=["<!-- END OF FRAGMENT -->"]
            )
        return response
    except Exception as e:
        print(f"Error in get_chat_completion: {e.__cause__}")
        return None

print("Inside LLM")

ruled_text_with_marker = ruled_text + "<!-- END OF FRAGMENT -->"

prompts = [
    {"role": "system", "content": (
            "You are an expert in XSLT 1.0. Simplify incomplete XSLT fragments using @* with name() filters. "
            "Always avoid repetition, avoid completing missing parts, and return only raw XML without markdown or commentary. "
            "Stop exactly at the end marker."
        ) },
    {"role": "user", "content": '''
                        CRITICAL INSTRUCTIONS:
                        1. Do not complete or close any tags—stop exactly at the marker below.
                        2. Simplify this XSLT fragment as much as possible using efficient XPath and XSLT 1.0 syntax.
                        3. If a value needs transformation (substring, boolean, number), apply it inline.
                        4. Use attribute wildcards (@*) and name() filters when applicable.
                        5. Keep the fragment exactly as given—do not add template wrappers or closing tags.
                        6. Return only the refined chunk without commentary or markdown./n'''},
    {"role": "user", "content": ruled_text_with_marker},
]

gpt_response = get_chat_completion(prompts,o3_mini_model_name)

llm_out = gpt_response.choices[0].message.content.strip()
import re
m = re.search(r'(<xsl:template[\s\S]*?</xsl:template>)', llm_out)
refined_llm = m.group(1) if m else llm_out
print(refined_llm)