import streamlit as st
import openai
from edgar import Company, set_identity

openai.api_key = st.secrets['OPENAI_API_KEY']

set_identity("Michael Mccallum mcalum@gmail.com")

def extact_cash_flow(ticker, type):
    cash_flow = Company(ticker).get_filings(form=type).latest(1).obj()
    return cash_flow.financials.cash_flow_statement.to_dataframe()

def extract_income_statement(ticker, type):
    income_statement = Company(ticker).get_filings(form=type).latest(1).obj()
    return income_statement.financials.income_statement.to_dataframe()

def extract_balance_sheet(ticker, type):
    balance_sheet = Company(ticker).get_filings(form=type).latest(1).obj()
    return balance_sheet.financials.balance_sheet.to_dataframe()
    
def generate_financial_summary(ticker, type):
    """
    Generate a summary of financial statements for the statements using GPT-3.5 Turbo or GPT-4.
    """
    summaries = []
    st.subheader("Cash Flow Summary")
    statement_type = "Cash Flow"
    cash_flow_summary = extact_cash_flow(ticker, type)
    summaries.append(f"{statement_type}:{cash_flow_summary}")
    st.dataframe(cash_flow_summary) 
    st.subheader("Income Statements Summary")
    statement_type = "Income Statement"
    income_statement_summary = extract_income_statement(ticker, type)
    summaries.append(f"{statement_type}:{income_statement_summary}")
    st.dataframe(income_statement_summary) 
    st.subheader("Balance Sheet Summary")
    statement_type = "Balance Sheet"
    balance_sheet_summary = extract_balance_sheet(ticker, type)
    summaries.append(f"{statement_type}:{balance_sheet_summary}")
    st.dataframe(balance_sheet_summary)   

    with st.spinner('Analyzing financial statements...'):
        # Call GPT-4 for analysis
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are an AI trained to provide financial analysis based on financial statements.",
                },
                {
                    "role": "user",
                    "content": f"""
                    Please analyze the following data and provide insights:\n{summaries}.\n 
                    Write each section out as instructed in the summary section and then provide analysis of how it's changed over the time period.
                    """
                }
            ]
        )

        return response['choices'][0]['message']['content']

def financial_statements():
    st.title('Trimble AI Financial Analysis')

    ticker = st.text_input("Please enter the company ticker:")

    if st.button('Run'):
        if ticker:
            ticker = ticker.upper()
            financial_summary = generate_financial_summary(ticker)
            st.write(f'Summary for {ticker}:\n {financial_summary}\n')
