from mNotProvided import \
    fbIsProvided, \
    fxGetFirstProvidedValue, \
    zNotProvided;

def cHTTPCookieStore_foClone(oSelf,
  *,
  fz0InvalidCookieAttributeCallback = zNotProvided, # (oCookieStore, oResponse, oURL, oHeader, sbCookieName, sbCookieValue, sbAttributeName, sb0AttributeValue, bIsNameKnown)
  fz0SetCookieCallback = zNotProvided, # (oCookieStore, oCookie, o0PreviousCookie)
  fz0CookieExpiredCallback = zNotProvided, # (oCookieStore, oCookie, o0PreviousCookie)
  fz0CookieAppliedCallback = zNotProvided, # (oCookieStore, oRequest, oURL, oCookie)
  fz0HeaderAppliedCallback = zNotProvided, # (oCookieStore, oRequest, oURL, oHeader)
  fz0CookieReceivedCallback = zNotProvided, # (oCookieStore, oResponse, oURL, oCookie)
  azoCookies = zNotProvided, 
):
  # Create a copy. If any arguments are provided, that copy will have the relevant properties
  # set to the value provided in the arguments instead of copied from the original.
  oClone = oSelf.__class__(
    f0InvalidCookieAttributeCallback = fxGetFirstProvidedValue(fz0InvalidCookieAttributeCallback, oSelf.f0InvalidCookieAttributeCallback),
    f0SetCookieCallback = fxGetFirstProvidedValue(fz0SetCookieCallback, oSelf.f0SetCookieCallback),
    f0CookieExpiredCallback = fxGetFirstProvidedValue(fz0CookieExpiredCallback, oSelf.f0CookieExpiredCallback),
    f0CookieAppliedCallback = fxGetFirstProvidedValue(fz0CookieAppliedCallback, oSelf.f0CookieAppliedCallback),
    f0HeaderAppliedCallback = fxGetFirstProvidedValue(fz0HeaderAppliedCallback, oSelf.f0HeaderAppliedCallback),
    f0CookieReceivedCallback = fxGetFirstProvidedValue(fz0CookieReceivedCallback, oSelf.f0CookieReceivedCallback),
  );
  if fbIsProvided(azoCookies):
    for oCookie in azoCookies:
      oClone.foAddCookie(oCookie);
  else:
    for aoCookies in oSelf.daoCookies_by_sbLowerDomainName.values():
      for oCookie in aoCookies:
        oClone.foAddCookie(oCookie);
  return oClone;