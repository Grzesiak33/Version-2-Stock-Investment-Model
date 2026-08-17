from .models import CompanyData

def catalyst_score(d):
    verified=d.metadata.get("verified_catalysts")
    n=len(verified) if isinstance(verified,list) else len(d.catalysts)
    return min(5.0, round(n*1.25,2))
def activity_score(d):
    vals=[v for v in (d.insider_activity,d.institutional_activity) if v is not None]
    if not vals:return 0.0
    norm=[max(0,min(1,(v+1)/2)) for v in vals]
    return round(5*sum(norm)/len(norm),2)
