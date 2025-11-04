################################# DOWNLOADING FILES FROM ORBIS #################################
### The goal is to write a script that logs in into Moody´s website, dowloads segments files and saves them to a local directory. 

### Structure of the script:
### 1. Log in into Moody's website
### 2. Writes the "Return to search bar" function
### 3. Loops through a list of companies, searches for each company, opens its profile, navigates to the segment data tab, and downloads the segment data file
### 4. Handles cases where no patent data is available
### 5. Saves the downloaded files to a specified directory
### 6. Logs out at the end (Remember to press Enter to close the browser at the end of the script)

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
import time
import os
import pandas as pd

download_dir = r"C:\Users\"  ### DEFINE YOUR DOWNLOAD DIRECTORY HERE
os.makedirs(download_dir, exist_ok=True)

options = Options()
options.add_argument("--start-maximized")
options.add_argument("--incognito")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)

# Force silent downloads to a known folder
prefs = {
    "download.default_directory": download_dir,
    "savefile.default_directory": download_dir,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True,
    "safebrowsing.disable_download_protection": True,
    "profile.default_content_setting_values.automatic_downloads": 1
}
options.add_experimental_option("prefs", prefs)

# Normal UA (use your real UA if you want)
options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)

driver = webdriver.Chrome(options=options)

# Hide common automation tells
driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
  "source": """
  Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
  Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
  Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3]});
  """
})

# Belt-and-suspenders: allow downloads via CDP (prevents Save As in Incognito)
try:
    driver.execute_cdp_cmd(
        "Page.setDownloadBehavior",
        {"behavior": "allow", "downloadPath": download_dir}
    )
except Exception:
    # Some Chrome builds ignore this; prefs above usually suffice.
    pass


######## KEY IDENTIFIERS ########
# Please double-check them 

EMAIL = "matilde.ciani@ifw-kiel.de" ## DEFINE YOUR USERNAME HERE
PASSWORD = "" ### DEFINE YOUR PASSWORD HERE

LOGOUT_URL ="" #### DEFINE YOUR LOGOUT PAGE HERE
input_dir = r"C:\Users\" ### DEFINE YOUR INPUT DIRECTORY HERE
INPUT_FILENAME = "FILE.xlsx" ### DEFINE YOUR INPUT FILENAME HERE
SHEET_NAME = "NA" ### DEFINE YOUR INPUT SHEET NAME HERE
COLUMN_NAME = "company_name" ### DEFINE YOUR INPUT COLUMN NAME HERE
MAXVALUE = 100 ### DEFINE THE MAXIMUM NUMBER OF COMPANIES TO PROCESS HERE (if you want to process all companies, set it to None)


#### DEFINING THE VECTOR OF COMPANIES TO PROCESS 

companies_with_no_data = []   ## Here we are going to store the companies that have no segment data available
company_identifiers = []   ### Here we are saving the orbis IDs
companies_not_found = []  ## Here we are going to store the companies that were not found in Orbis


input_excel_path = os.path.join(input_dir, INPUT_FILENAME)
df_companies = pd.read_excel(input_excel_path, dtype={COLUMN_NAME: str}) ## I am removing the Sheet Name option sheet_name=SHEET_NAME,

# Drop blanks and duplicates, convert to string
company_name = (
    df_companies[COLUMN_NAME]
    .dropna()
    .drop_duplicates()
    .astype(str)
    .tolist()[:MAXVALUE]  
)

# ALTERNATIVELY, you can define your companies manually:
#company_name = ["016814229", "549792643"]    ## DEFINE YOUR COMPANIES HERE (Orbis IDs)

############ ACTUAL SCRIPT STARTS HERE ##########

wait = WebDriverWait(driver, 30) ### Generally the wait time is 30 seconds, unless the element is found earlier
actions = ActionChains(driver)

########## LOG IN INTO ORBIS ##########

try:
    # Go to the login page
    driver.get("https://login.bvdinfo.com/login")

    # Find the email/username field (input inside "Log in" box)
    username_field = wait.until(
        EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Username"]'))
    )
    username_field.send_keys(EMAIL) ## Insert your email here
    time.sleep(0.5)  ## Wait for a bit to ensure the input is registered

    # Click the Continue button
    continue_button = wait.until(
        EC.element_to_be_clickable((By.XPATH, '//button[text()="Continue"]'))
    )
    continue_button.click()

    print("Username submitted successfully :) ")

     # Wait for the Password field to appear
    password_field = wait.until(
    EC.visibility_of_element_located((By.XPATH, '//input[@placeholder="Password"]'))
    )
    password_field.send_keys(PASSWORD) ## Here we put your password

    # Click the "Log in" button
    login_button = wait.until(
        EC.element_to_be_clickable((By.XPATH, '//button[text()="Log in"]'))
    )
    login_button.click()

    print("✅ Password submitted")

    # Wait for "ORBIS" link/button to appear
    orbis_link = wait.until(
        EC.element_to_be_clickable((By.XPATH, '//a[contains(text(), "ORBIS")]'))
    )
    orbis_link.click()
    print("✅ Successfully logged in to ORBIS")

except Exception as e:
    print("Did not fully go through with it :( ", e)

time.sleep(1.2)

#################################################
############# RETURN TO SEARCH BAR ###########
#################################################

def return_to_search_bar():
    try:
        search_icon = wait.until(EC.element_to_be_clickable((
            By.XPATH,
            "//li[contains(@class, 'search')]//a"
        )))
        driver.execute_script("arguments[0].scrollIntoView(true);", search_icon)
        driver.execute_script("arguments[0].click();", search_icon)
        print("🔁 Returned to search bar")
    except Exception as e:
        print("❌ Could not return to search bar:", e)


#########################################################
############# BEGINNING OF LOOP ####
#########################################################


def process_company(company):
    print(f"🔍 Processing company: {company}")

    #### FIND THE COMPANY NAME 
    try:
        findcompany_field = wait.until(
            EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Find a company"]'))
        )
        findcompany_field.clear()
        findcompany_field.send_keys(company)
        time.sleep(0.5)

        # Press Enter twice
        findcompany_field.send_keys(u'\ue007')
        time.sleep(0.5)
        findcompany_field.send_keys(u'\ue007')
        print(f"✅ {company} submitted")

    except Exception as e:
        print(f"❌ {company} not submitted:", e)
        
    ### We wait for the results to load
    # Click the first result (suggestions panel)
    try:
        first_link = wait.until(EC.element_to_be_clickable((
            By.XPATH, "(//p[@class='name']/ancestor::a)[1]"
        )))
        driver.execute_script("arguments[0].click();", first_link)
        print("✅ First result clicked from list")

    except Exception:
        # QUICK check for explicit "not found" message (no long wait)
        try:
            WebDriverWait(driver, 2).until(
                lambda d: d.find_elements(By.XPATH, "//*[contains(text(), 'The company was not found')]") or
                        d.find_elements(By.XPATH, "(//p[@class='name']/ancestor::a)[1]")
            )
        except TimeoutException:
            pass

        if driver.find_elements(By.XPATH, "//*[contains(text(), 'The company was not found')]"):
            print(f"❌ Company not found in Orbis: {company}")
            companies_not_found.append(company)
            print(f"✅ {company} added to not found list")
            return_to_search_bar()
            return

        # Fallback: try selecting via keyboard
        try:
            findcompany_field.send_keys(Keys.ARROW_DOWN)
            time.sleep(0.2)
            findcompany_field.send_keys(Keys.ENTER)
            print(f"✅ {company} manually selected")
        except Exception as e2:
            print(f"❌ Could not select {company} from suggestions: {e2}")
            companies_not_found.append(company)
            print(f"✅ {company} added to not found list")
            return_to_search_bar()
            return


    ### SAVING ORBIS ID NUMBER.
    try: 
        # Company name cell (left fixed table)
        company_name_element = wait.until(
            EC.presence_of_element_located((
                By.XPATH, "//table[contains(@class, 'fixed-data')]//tr[contains(@class, 'oneline')][1]//td[contains(@class, 'columnAlignLeft')]//a[@data-action='reporttransfer']"
            ))
        )

        # Orbis ID number cell (right scroll table)
        orbis_id_element = wait.until(
            EC.presence_of_element_located((
                By.XPATH, "//table[contains(@class, 'scroll-data')]//tr[1]/td[contains(@class, 'columnAlignLeft')][1]"
            ))
        )
        print(orbis_id_element.text)

        # Make sure text is populated (grid often paints before text arrives)
        WebDriverWait(driver, 10).until(lambda d: company_name_element.text.strip() and orbis_id_element.text.strip())

        orbis_company_name = company_name_element.text.strip()
        orbis_id = orbis_id_element.text.strip()
        print(f"📌 Found: {orbis_company_name} | Orbis ID: {orbis_id}")

        # Instead of writing now, store in memory
        company_identifiers.append({"Company Name": orbis_company_name, "Orbis ID": orbis_id})

    except Exception as e:
        print(f"❌ Failed to read/save row for {company}:", e)


    #### OPENING COMPANY PROFILE
    try:
        first_company_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//table[contains(@class, 'fixed-data')]//tr[contains(@class, 'oneline')][1]//td[contains(@class, 'columnAlignLeft')]//a[@data-action='reporttransfer']"))
        )
        first_company_link.click()
        print(f"✅ {company} profile page opened successfully")
    except Exception as e:
        print(f"❌ {company} page not opened:", e)
        return_to_search_bar()
        print(f"❌ {company} not downloaded")
        return

    ### SELECTING INTELLECTUAL PROPERTY TAB

    try:
        # Wait for the outer scroll container that controls the sidebar scrolling
        sidebar_outer = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.scroll"))
        )

        # Manually scroll it a few times to make sure the tab becomes visible
        for _ in range(5):
            driver.execute_script("arguments[0].scrollTop += 200;", sidebar_outer)
            time.sleep(0.5)  # Small delay for DOM to update

        # Now find and click the Intellectual property tab
        intellectual_tab = wait.until(
            EC.element_to_be_clickable((
                By.XPATH, "//a[@role='treeitem' and @title='Intellectual property']"
            ))
        )
        intellectual_tab.click()
        print(f"✅ Opened 'Intellectual property' tab for {company}")

    except Exception as e:
        print(f"❌ Could not open 'Intellectual property' for {company}:", e)
        return_to_search_bar()
        print(f"❌ {company} not downloaded")
        return

    
    ## SELECTING PATENT SEGMENT TAB 
    try:
        segment_data_tab = wait.until(EC.element_to_be_clickable((
            By.XPATH,
            "//a[@role='treeitem' and @title='Patent portfolio']"
        )))
        driver.execute_script("arguments[0].scrollIntoView(true);", segment_data_tab)
        driver.execute_script("arguments[0].click();", segment_data_tab)
        print("✅ Opened 'Patent data'")
    except Exception as e:
        print("❌ Could not open 'Patent Data':", e)
        companies_with_no_data.append(company)
        return_to_search_bar()
        print(f"❌ {company} not downloaded")
        return


    ### WAIT FOR TOTAL DATA OR NO DATA APPEAR

    try:
        print(f"⏳ Waiting for result (data or no-data) for {company}...")

        WebDriverWait(driver, 300).until(
            lambda d: d.find_elements(By.XPATH, "//td[contains(text(), 'No data available')]") or
                    d.find_elements(By.XPATH, "//td[contains(text(), 'Total number of patents')]")
        )

        if driver.find_elements(By.XPATH, "//td[contains(text(), 'No data available')]"):
            print(f"⚠️ No data available for {company}. Skipping...")
            companies_with_no_data.append(company)
            return_to_search_bar()
            return

        if driver.find_elements(By.XPATH, "//td[contains(text(), 'Total number of patents')]"):
            print(f"✅ Patent data found for {company}. Proceeding...")

    except TimeoutException:
        print(f"❌ Timed out after 120 seconds waiting for patent data for {company}. Skipping...")
        companies_with_no_data.append(company)
        return_to_search_bar()
        return
    
    ## CLICK ON DOWNLOAD BUTTON 
    try:
        print(f"🔍 Scrolling and locating correct Export button...")

        # Scroll down a bit to reveal the correct section
        driver.execute_script("window.scrollBy(0, 800);")
        time.sleep(1)

        # Find the correct Export to Excel button within that section
        excel_button_export = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Excel']/parent::a")))

        # Scroll and click
        excel_button_export.click()

        print("📥 Clicked correct Export to Excel button.")

    except Exception as e:
        print(f"❌ Could not click segment Excel icon for {company}: {e}")
        companies_with_no_data.append(company)
        return_to_search_bar()
        print(f"{company} not downloaded")
        return
    

    ### INSERT NAME OF THE FILE 

    try: 
        driver.execute_script("window.scrollTo(0, 800);") 
        name_input = wait.until(EC.presence_of_element_located((
            By.ID, "component_FileName")))
        name_input.clear()
        ## We insert Business Segment data: "COMPANY_NAME"
        name_input.send_keys(f"PatentData_{company}")
        print(f"✅ Set file name for {company} to 'PatentData_{company}'")

    except Exception as e:
        print("❌ Could not set the file name:", e)

    time.sleep(1)  # Wait for the input to be registered

    #### CLICK ON EXPORT

    try: 
        export_button = wait.until(EC.element_to_be_clickable((
        By.XPATH, "//a[contains(@class, 'button') and contains(@class, 'submit') and contains(text(), 'Export')]"
        )))
        driver.execute_script("arguments[0].scrollIntoView(true);", export_button)
        driver.execute_script("arguments[0].click();", export_button)
        print("✅ Clicked 'Export' button for", company)

    except Exception as e:
        print("❌ Could not click 'Export' button:", e)    

    time.sleep(1)  # Wait for the click to be registered

    ## WAIT FOR THE DOWNLOAD TO COMPLETE
    print(f"⏳ Waiting for download to be ready for {company}...")

    try:
        WebDriverWait(driver, 1200).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[contains(text(), 'Your export is now ready for download')]")
            )
        )
        print(f"✅ Download ready for {company}")

    except Exception as e:
        print("❌ File not downloaded", e)
        companies_with_no_data.append(company)

    time.sleep(1)  # Allow time for any additional actions to happen

    # CLOSE THE POPUP (don’t click outside; click the 'x') ===
    print("🔍 Attempting to close download pop-up...")
    try:
           # Try JS-click on the real X (bypasses hit-testing)
            x_img = wait.until(EC.presence_of_element_located((
                By.CSS_SELECTOR, "img.close.px16[role='button'][aria-label*='Close']"
            )))
            driver.execute_script("arguments[0].click();", x_img)

            # Confirm it actually closed
            WebDriverWait(driver, 3).until(EC.invisibility_of_element_located(
                    (By.CSS_SELECTOR, ".popup.popup__dialog[style*='display: block']")
                ))
            print("✅ Popup closed via JS click on X")

    except Exception as e:
            print("❌ Could not close pop-up by clicking outside:", e)


    ### RETURN TO SEARCH

    try:
        return_to_search_bar()
        print("✅ Returned to search bar")

    except Exception as e:
        print("❌ Could not return to search bar:", e)



#########################################################
################ END OF LOOP ####
#########################################################


### RUNNING THE LOOP 
try: 
    for company in company_name:
        process_company(company)
    print("✅✅✅ All companies processed successfully")

    ### Download companies with no data

    if companies_with_no_data:
        df = pd.DataFrame(companies_with_no_data, columns=["Orbis_ID"])
        df.to_excel(os.path.join(download_dir, "no_data_companies.xlsx"), index=False)
        print(f"\n✅✅ Saved list of companies with no data to: {download_dir}\\no_data_companies.xlsx")
    else:
        print("\n✅✅ Data was available for all companies.")

    if company_identifiers:
        out_file = os.path.join(download_dir, "CompanyIdentifiers.xlsx")
        pd.DataFrame(company_identifiers).to_excel(out_file, index=False)
        print(f"💾 All company identifiers saved to {out_file}")
    else:
        print("⚠️ No company identifiers to save.")

    if companies_not_found:
        nf_path = os.path.join(download_dir, "no_company_data.xlsx")
        pd.DataFrame(companies_not_found, columns=["company_name"]).to_excel(nf_path, index=False)
        print(f"💾 Saved companies not found to {nf_path}")    

    else:
        print("✅ All companies were found in Orbis.")

except Exception as e:
    ## Print name of last company processed
    print(f"❌ An error occurred while processing {company}: {e}")

finally:
    input("👀 Press Enter to close the browser...")

    # Go to logout page
    driver.get(LOGOUT_URL)
    time.sleep(2)

    driver.quit()



