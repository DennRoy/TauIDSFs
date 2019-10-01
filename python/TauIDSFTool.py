# Author: Izaak Neutelings (July 2019)
# https://twiki.cern.ch/twiki/bin/viewauth/CMS/TauIDRecommendation13TeV
import os
from TauPOG.TauIDSFs import ensureTFile, extractTH1
datapath = os.environ['CMSSW_BASE']+"/src/TauPOG/TauIDSFs/data"

class TauIDSFTool:
    
    def __init__(self, year, id, wp='Tight', dm=False):
        """Choose the IDs and WPs for SFs. For available tau IDs and WPs, check
        https://cms-nanoaod-integration.web.cern.ch/integration/master-102X/mc102X_doc.html#Tau"""
        
        years = ['2016Legacy','2017ReReco','2018ReReco']
        assert year in years, "You must choose a year from %s."%(', '.join(years))
        self.ID = id
        self.WP = wp
        
        if id in ['MVAoldDM2017v2','DeepTau2017v2p1']:
          if dm:
            file = ensureTFile("%s/TauID_SF_dm_%s_%s.root"%(datapath,id,year))
            self.hist = extractTH1(file,wp)
            self.hist.SetDirectory(0)
            file.Close()
            self.DMs = [0,1,10]
            self.getSFvsPT  = self.disabled
            self.getSFvsEta = self.disabled
          else:
            file = ensureTFile("%s/TauID_SF_pt_%s_%s.root"%(datapath,id,year))
            self.func         = { }
            self.func[None]   = file.Get("%s_cent"%(wp))
            self.func['Up']   = file.Get("%s_up"%(wp))
            self.func['Down'] = file.Get("%s_down"%(wp))
            file.Close()
            self.getSFvsDM  = self.disabled
            self.getSFvsEta = self.disabled
        elif id in ['antiMu3','antiEleMVA6']:
            file = ensureTFile("%s/TauID_SF_eta_%s_%s.root"%(datapath,id,year))
            self.hist = extractTH1(file,wp)
            self.hist.SetDirectory(0)
            file.Close()
            self.genmatches = [1,3] if 'ele' in id.lower() else [2,4]
            self.getSFvsPT  = self.disabled
            self.getSFvsDM  = self.disabled
        else:
          raise IOError("Did not recognize tau ID '%s'!"%id)
        
    def getSFvsPT(self, pt, genmatch=5, unc=None):
        """Get tau ID SF vs. tau pT."""
        if genmatch==5:
          return self.func[unc].Eval(pt)
        return 1.0
        
    def getSFvsDM(self, pt, dm, genmatch=5, unc=None):
        """Get tau ID SF vs. tau DM."""
        if dm in self.DMs or pt<40:
          if genmatch==5:
            bin = self.hist.GetXaxis().FindBin(dm)
            SF  = self.hist.GetBinContent(bin)
            if unc=='Up':
              SF += self.hist.GetBinError(bin)
            elif unc=='Down':
              SF -= self.hist.GetBinError(bin)
            return SF
          return 1.0
        return 0.0
        
    def getSFvsEta(self, eta, genmatch, unc=None):
        """Get tau ID SF vs. tau eta."""
        eta = abs(eta)
        if genmatch in self.genmatches:
          bin = self.hist.GetXaxis().FindBin(eta)
          SF  = self.hist.GetBinContent(bin)
          if unc=='Up':
            SF += self.hist.GetBinError(bin)
          elif unc=='Down':
            SF -= self.hist.GetBinError(bin)
          return SF
        return 1.0
        
    @staticmethod
    def disabled(*args,**kwargs):
        raise AttributeError("Disabled method.")
    
