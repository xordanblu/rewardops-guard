Class RewardOps.FHIR.CareBriefAgent Extends %RegisteredObject
{

ClassMethod Name() As %String
{
    Quit "FHIR Care Brief Agent"
}

ClassMethod SummaryRoles() As %String
{
    Quit "ed_doctor,care_manager,patient,family_caregiver"
}

ClassMethod ContestFit() As %String
{
    Quit "Smart Patient Summary Generator with medication safety and care plan task outputs"
}

}
