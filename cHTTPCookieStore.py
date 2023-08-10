import re;

from .cHTTPCookie import cHTTPCookie;
from .cHTTPCookieStore_faoGetCookiesForURL import cHTTPCookieStore_faoGetCookiesForURL;
from .cHTTPCookieStore_fApplyToRequestForURL import cHTTPCookieStore_fApplyToRequestForURL;
from .cHTTPCookieStore_fbImportFromJSON import cHTTPCookieStore_fbImportFromJSON;
from .cHTTPCookieStore_fbRemoveCookie import cHTTPCookieStore_fbRemoveCookie;
from .cHTTPCookieStore_fdxExportToJSON import cHTTPCookieStore_fdxExportToJSON;
from .cHTTPCookieStore_foAddCookie import cHTTPCookieStore_foAddCookie;
from .cHTTPCookieStore_foClone import cHTTPCookieStore_foClone;
from .cHTTPCookieStore_fUpdateFromResponseAndURL import cHTTPCookieStore_fUpdateFromResponseAndURL;

rbEOL = re.compile(rb"[\r\n]+");

class cHTTPCookieStore(object):
  @classmethod
  def foFromNetscapeFileFormat(cClass, sbLines):
    oCookieStore = cClass();
    for sbLine in rbEOL.split(sbLines):
      sbLineStripped = sbLine.strip();
      if sbLineStripped != b"" and not sbLineStripped.startswith(b"#"):
        oCookie = cHTTPCookie.foFromNetscapeFileFormat(sbLine);
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
        oCookie = cHTTPCookie.foFromNetscapeFileFormat(sbLine);
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

  faoGetCookiesForURL = cHTTPCookieStore_faoGetCookiesForURL;
  fApplyToRequestForURL = cHTTPCookieStore_fApplyToRequestForURL;
  fbImportFromJSON = cHTTPCookieStore_fbImportFromJSON;
  fbRemoveCookie = cHTTPCookieStore_fbRemoveCookie;
  fdxExportToJSON = cHTTPCookieStore_fdxExportToJSON;
  foAddCookie = cHTTPCookieStore_foAddCookie;
  foClone = cHTTPCookieStore_foClone;
  fUpdateFromResponseAndURL = cHTTPCookieStore_fUpdateFromResponseAndURL;
