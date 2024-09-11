from pydantic import BaseModel, Field, HttpUrl
from typing import Any, Optional
from datetime import datetime


class Opportunity(BaseModel):
    AccountId: str
    Name: str
    additional_fields: dict[str, Any] = Field(default_factory=dict)

    class Config:
        extra = "allow"

    def __init__(self, **data):
        known_fields = {
            key: data.pop(key) for key in ("AccountId", "Name") if key in data
        }
        super().__init__(**known_fields)
        self.additional_fields = data


class Account(BaseModel):
    type: str
    url: HttpUrl
    Id: str
    IsDeleted: bool
    MasterRecordId: Optional[str] = None
    Name: str
    LastName: Optional[str] = None
    FirstName: Optional[str] = None
    Salutation: Optional[str] = None
    Type: Optional[str] = None
    RecordTypeId: Optional[str] = None
    ParentId: Optional[str] = None
    BillingStreet: Optional[str] = None
    BillingCity: Optional[str] = None
    BillingState: Optional[str] = None
    BillingPostalCode: Optional[str] = None
    BillingCountry: Optional[str] = None
    BillingLatitude: Optional[float] = None
    BillingLongitude: Optional[float] = None
    BillingGeocodeAccuracy: Optional[str] = None
    BillingAddress: Optional[str] = None
    ShippingStreet: Optional[str] = None
    ShippingCity: Optional[str] = None
    ShippingState: Optional[str] = None
    ShippingPostalCode: Optional[str] = None
    ShippingCountry: Optional[str] = None
    ShippingLatitude: Optional[float] = None
    ShippingLongitude: Optional[float] = None
    ShippingGeocodeAccuracy: Optional[str] = None
    ShippingAddress: Optional[str] = None
    Phone: Optional[str] = None
    Fax: Optional[str] = None
    Website: Optional[HttpUrl] = None
    PhotoUrl: Optional[HttpUrl] = None
    Industry: Optional[str] = None
    AnnualRevenue: Optional[float] = None
    NumberOfEmployees: Optional[int] = None
    Description: Optional[str] = None
    OwnerId: Optional[str] = None
    CreatedDate: Optional[datetime] = None
    CreatedById: Optional[str] = None
    LastModifiedDate: Optional[datetime] = None
    LastModifiedById: Optional[str] = None
    SystemModstamp: Optional[datetime] = None
    LastActivityDate: Optional[datetime] = None
    LastViewedDate: Optional[datetime] = None
    LastReferencedDate: Optional[datetime] = None
    IsPartner: Optional[bool] = None
    IsCustomerPortal: Optional[bool] = None
    PersonContactId: Optional[str] = None
    IsPersonAccount: Optional[bool] = None
    PersonMailingStreet: Optional[str] = None
    PersonMailingCity: Optional[str] = None
    PersonMailingState: Optional[str] = None
    PersonMailingPostalCode: Optional[str] = None
    PersonMailingCountry: Optional[str] = None
    PersonMailingLatitude: Optional[float] = None
    PersonMailingLongitude: Optional[float] = None
    PersonMailingGeocodeAccuracy: Optional[str] = None
    PersonMailingAddress: Optional[str] = None
    PersonOtherStreet: Optional[str] = None
    PersonOtherCity: Optional[str] = None
    PersonOtherState: Optional[str] = None
    PersonOtherPostalCode: Optional[str] = None
    PersonOtherCountry: Optional[str] = None
    PersonOtherLatitude: Optional[float] = None
    PersonOtherLongitude: Optional[float] = None
    PersonOtherGeocodeAccuracy: Optional[str] = None
    PersonOtherAddress: Optional[str] = None
    PersonMobilePhone: Optional[str] = None
    PersonHomePhone: Optional[str] = None
    PersonOtherPhone: Optional[str] = None
    PersonAssistantPhone: Optional[str] = None
    PersonEmail: Optional[str] = None
    PersonTitle: Optional[str] = None
    PersonDepartment: Optional[str] = None
    PersonAssistantName: Optional[str] = None
    PersonLeadSource: Optional[str] = None
    PersonBirthdate: Optional[datetime] = None
    PersonLastCURequestDate: Optional[datetime] = None
    PersonLastCUUpdateDate: Optional[datetime] = None
    PersonEmailBouncedReason: Optional[str] = None
    PersonEmailBouncedDate: Optional[datetime] = None
    PersonIndividualId: Optional[str] = None
    Jigsaw: Optional[str] = None
    JigsawCompanyId: Optional[str] = None
    AccountSource: Optional[str] = None
    SicDesc: Optional[str] = None
    Technical_Notes__c: Optional[str] = None
    Current_Workflow_System__c: Optional[str] = None
    Gong__Gong_Count__c: Optional[float] = None
    Portal_Account_Access__c: Optional[str] = None
    Billing_Email__c: Optional[str] = None
    Max_New_Renew_Close_Date__c: Optional[datetime] = None
    Prefect_Tenant_Slug__c: Optional[str] = None
    Billable_Task_Run_Balance__c: Optional[float] = None
    Looker_Stats_Link__c: Optional[str] = None
    Out_of_Billable_Task_Runs_Date__c: Optional[datetime] = None
    Last_Low_Run_Alert_Date__c: Optional[datetime] = None
    Activation_Score_with_Link__c: Optional[str] = None
    Prefect_Cloud_License_ID__c: Optional[str] = None
    Cohort__c: Optional[str] = None
    Stripe_Customer_Id__c: Optional[str] = None
    Company_Name_PA__c: Optional[str] = None
    Influencer__c: Optional[bool] = None
    Support_Tier__c: Optional[str] = None
    User_ID__c: Optional[str] = None
    Customer_Success_Manager__c: Optional[str] = None
    No_Gifts__c: Optional[bool] = None
    Cloud_1_Tenant_ID__c: Optional[str] = None
    ProServ_Hours_Purchased__c: Optional[bool] = None
    Solutions_Engineer__c: Optional[str] = None
    X18_Character_ID__c: Optional[str] = None
    Onboarding_Tags__c: Optional[str] = None
    xbeamprod__Available_Overlaps__c: Optional[str] = None
    Cloud1_License__c: Optional[str] = None
    Cloud2_Account__c: Optional[str] = None
    Converted_Type__c: Optional[str] = None
    UniqueEntry__Account_Dupes_Ignored__c: Optional[str] = None
    UniqueEntry__Current_Endpoint__c: Optional[str] = None
    UniqueEntry__EnrichedOn__c: Optional[datetime] = None
    UniqueEntry__RingLead_App_Field__c: Optional[str] = None
    UniqueEntry__RingLead_Enrichment_Result__c: Optional[str] = None
    UniqueEntry__RingLead_Last_Processed_Date__c: Optional[datetime] = None
    UniqueEntry__Ringlead_Id__c: Optional[str] = None
    UniqueEntry__isRingLeadEnriched__c: Optional[bool] = None
    Closed_Won_Opps__c: Optional[float] = None
    Support_Engineer__c: Optional[str] = None
    Sales_Engineer__c: Optional[str] = None
    Enterprise_License_Admin_Email__c: Optional[str] = None
    Prefect_Cloud_Account_ID__c: Optional[str] = None
    Prefect_Cloud_Audit_Log_Retention__c: Optional[float] = None
    Prefect_Cloud_Automations__c: Optional[str] = None
    Prefect_Cloud_Custom_Workspace_Roles__c: Optional[bool] = None
    Prefect_Cloud_Directory_Sync__c: Optional[bool] = None
    Prefect_Cloud_Flow_Run_Retention__c: Optional[float] = None
    Prefect_Cloud_Users__c: Optional[int] = None
    Prefect_Cloud_Workspaces__c: Optional[int] = None
    Support_Only__c: Optional[bool] = None
    No_Employees_E__c: Optional[int] = None
    Industry_E__c: Optional[str] = None
    Annual_Revenue_E__c: Optional[float] = None
    Website_E__c: Optional[HttpUrl] = None
    Phone_E__c: Optional[str] = None
    ZoomInfo_Company_ID__c: Optional[str] = None
    Subscription_Type__c: Optional[str] = None
    LID__LinkedIn_Company_Id__c: Optional[str] = None
    Secondary_Website__c: Optional[HttpUrl] = None
    Subscription_Status__c: Optional[str] = None
    IsActive__c: Optional[bool] = None
    Outreach_ID__c: Optional[str] = None
    Type__pc: Optional[str] = None
    Secondary_Email__pc: Optional[str] = None
    Use_Case__pc: Optional[str] = None
    Date_Added__pc: Optional[datetime] = None
    Do_Not_Contact__pc: Optional[bool] = None
    Audience_Tag__pc: Optional[str] = None
    SupportTier__pc: Optional[str] = None
    Cloud1_User__pc: Optional[str] = None
    Cloud2_User__pc: Optional[str] = None
    Converted_Type__pc: Optional[str] = None
    UniqueEntry__Contact_Dupes_Ignored__pc: Optional[str] = None
    UniqueEntry__Current_Endpoint__pc: Optional[str] = None
    UniqueEntry__EnrichedOn__pc: Optional[datetime] = None
    UniqueEntry__Lead_Dupes_Ignored__pc: Optional[str] = None
    UniqueEntry__RingLead_App_Field__pc: Optional[str] = None
    UniqueEntry__RingLead_Last_Processed_Date__pc: Optional[datetime] = None
    UniqueEntry__Ringlead_Id__pc: Optional[str] = None
    Former_Employee__pc: Optional[bool] = None
    Enrich_Archive__pc: Optional[str] = None
    LID__LinkedIn_Company_Id__pc: Optional[str] = None
    LID__LinkedIn_Member_Token__pc: Optional[str] = None
    LID__No_longer_at_Company__pc: Optional[bool] = None
    LogRocket_Sessions__pc: Optional[str] = None
    NektarActions__pc: Optional[str] = None
    NektarJobChange__pc: Optional[bool] = None
    Campaign_Name__pc: Optional[str] = None
    Touchpoint_Guide__pc: Optional[str] = None
