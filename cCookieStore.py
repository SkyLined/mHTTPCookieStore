import re;

from .cCookie import cCookie;
from .cCookieStore_faoGetCookies import cCookieStore_faoGetCookies;
from .cCookieStore_faoGetCookiesForURL import cCookieStore_faoGetCookiesForURL;
from .cCookieStore_fApplyToRequestForURL import cCookieStore_fApplyToRequestForURL;
from .cCookieStore_fbImportFromJSON import cCookieStore_fbImportFromJSON;
from .cCookieStore_fbRemoveCookie import cCookieStore_fbRemoveCookie;
from .cCookieStore_fdxExportToJSON import cCookieStore_fdxExportToJSON;
from .cCookieStore_foAddCookie import cCookieStore_foAddCookie;
from .cCookieStore_foClone import cCookieStore_foClone;
from .cCookieStore_fUpdateFromResponseAndURL import cCookieStore_fUpdateFromResponseAndURL;

rbEOL = re.compile(rb"[\r\n]+");

class cCookieStore(object):
  @classmethod
  def foFromNetscapeFileFormat(cClass, sbLines):
    oCookieStore = cClass();
    for sbLine in rbEOL.split(sbLines):
      sbLineStripped = sbLine.strip();
      if sbLineStripped != b"" and not sbLineStripped.startswith(b"#"):
        oCookie = cCookie.foFromNetscapeFileFormat(sbLine);
        oCookieStore.foAddCookie(oCookie);
    return oCookieStore;

  def __init__(oSelf,
    *,
    f0InvalidCookieAttributeCallback = None, # (oCookieStore, oResponse, oURL, oHeader, sbCookieName, sbCookieValue, sbAttributeName, sb0AttributeValue, bIsNameKnown)
    f0SetCookieCallback = None, # (oCookieStore, oCookie, o0PreviousCookie)
    f0CookieExpiredCallback = None, # (oCookieStore, oCookie, o0PreviousCookie)
    f0CookieAppliedCallback = None, # (oCookieStore, oRequest, oURL, oCookie)
    f0HeaderAppliedCallback = None, # (oCookieStore, oRequest, oURL, oHeader)
    f0CookieReceivedCallback = None, # (oCookieStore, oResponse, oURL, oCookie)
  ):
    oSelf.f0InvalidCookieAttributeCallback = f0InvalidCookieAttributeCallback;
    oSelf.f0SetCookieCallback = f0SetCookieCallback;
    oSelf.f0CookieExpiredCallback = f0CookieExpiredCallback;
    oSelf.f0CookieAppliedCallback = f0CookieAppliedCallback;
    oSelf.f0HeaderAppliedCallback = f0HeaderAppliedCallback;
    oSelf.f0CookieReceivedCallback = f0CookieReceivedCallback;
    oSelf.daoCookies_by_sbLowerDomainName = {};

  def fuAddFromNetscapeFileFormat(oSelf, sbLines):
    uCookiesAdded = 0;
    for sbLine in rbEOL.split(sbLines):
      sbLineStripped = sbLine.strip();
      if sbLineStripped != b"" and not sbLineStripped.startswith(b"# "):
        oCookie = cCookie.foFromNetscapeFileFormat(sbLine);
        oSelf.foAddCookie(oCookie);
        uCookiesAdded += 1;
    return uCookiesAdded;
  
  def fasGetDetails(oSelf):
    uTotalCookies = sum(len(aoCookies) for aoCookies in oSelf.daoCookies_by_sbLowerDomainName.values());
    return [
      "%d cookies for %d domains" % (uTotalCookies, len(oSelf.daoCookies_by_sbLowerDomainName)),
    ];
  
  def __repr__(oSelf):
    sModuleName = ".".join(oSelf.__class__.__module__.split(".")[:-1]);
    return "<%s.%s#%X|%s>" % (sModuleName, oSelf.__class__.__name__, id(oSelf), "|".join(oSelf.fasGetDetails()));
  
  def __str__(oSelf):
    return "%s#%X{%s}" % (oSelf.__class__.__name__, id(oSelf), ", ".join(oSelf.fasGetDetails()));

  faoGetCookies = cCookieStore_faoGetCookies;
  faoGetCookiesForURL = cCookieStore_faoGetCookiesForURL;
  fApplyToRequestForURL = cCookieStore_fApplyToRequestForURL;
  fbImportFromJSON = cCookieStore_fbImportFromJSON;
  fbRemoveCookie = cCookieStore_fbRemoveCookie;
  fdxExportToJSON = cCookieStore_fdxExportToJSON;
  foAddCookie = cCookieStore_foAddCookie;
  foClone = cCookieStore_foClone;
  fUpdateFromResponseAndURL = cCookieStore_fUpdateFromResponseAndURL;
