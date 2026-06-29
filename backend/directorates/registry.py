from backend.directorates.legacy import DIRECTORATE as LegacyDirectorate
from backend.directorates.investor_intelligence import DIRECTORATE as InvestorIntelligenceDirectorate

DIRECTORATES = {
    "Commander": None,
    "Engineering": None,
    "Forge": None,
    "Legacy": LegacyDirectorate,
    "Investor Intelligence": InvestorIntelligenceDirectorate,
    "Cyber Intelligence": None,
    "Medical Intelligence": None,
    "Financial Intelligence": None,
    "Intelligence": None,
    "Security": None,
    "Education": None,
    "Operations": None,
    "Communications": None,
    "Logistics": None,
    "Research": None,
    "Family Office": None,
}
