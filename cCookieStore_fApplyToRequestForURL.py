from mHTTPProtocol import cHeader;

bDebugOutput = False;

def cCookieStore_fApplyToRequestForURL(oSelf, oRequest, oURL):
  if bDebugOutput: print(",-- Applying session headers ".ljust(80, "-"));
  # Cookies
  asbCookieHeaderElements = [];
  if oSelf.daoCookies_by_sbLowerDomainName and bDebugOutput: print("|-- Cookies ".ljust(80, "-"));
  for oCookie in oSelf.faoGetCookiesForURL(oURL):
    if bDebugOutput: print("| + Cookie applied: %s" % oCookie);
    asbCookieHeaderElements.append(b"%s=%s" % (oCookie.sbName, oCookie.sbValue));
    if oSelf.f0CookieAppliedCallback:
      oSelf.f0CookieAppliedCallback(oSelf, oRequest, oURL, oCookie);
  if len(asbCookieHeaderElements) > 0:
    sbCookieHeader = b"; ".join(asbCookieHeaderElements);
    if bDebugOutput: print("| Cookie: %s" % repr(sbCookieHeader)[1:]);
    oHeader = cHTTPHeader(b"Cookie", sbCookieHeader);
    oRequest.oHeaders.fAddHeader(oHeader);
    if oSelf.f0HeaderAppliedCallback:
      oSelf.f0HeaderAppliedCallback(oSelf, oRequest, oURL, oHeader);
