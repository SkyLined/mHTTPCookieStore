from .cHTTPCookie import cHTTPCookie;

def cHTTPCookieStore_foAddCookie(oSelf, *txArgs, **dxArgs):
  if len(txArgs) == 1 and len(dxArgs) == 0 and isinstance(txArgs[0], cHTTPCookie):
    oCookie = txArgs[0];
  else:
    oCookie = cHTTPCookie(*txArgs, **dxArgs)
  sbLowerCookieDomainName = oCookie.sbDomainName.lower();
  aoExistingCookies_for_sbLowerDomainName = oSelf.daoCookies_by_sbLowerDomainName.setdefault(sbLowerCookieDomainName, []);
  # This can replace or remove an existing cookie with the same name:
  # TODO: should this really be case-sensitive?
  o0PreviousCookie = None;
  for oExistingCookie in aoExistingCookies_for_sbLowerDomainName:
    if oExistingCookie.sbName == oCookie.sbName:
      aoExistingCookies_for_sbLowerDomainName.remove(oExistingCookie);
      o0PreviousCookie = oExistingCookie;
  if oCookie.fbIsExpired():
    if oSelf.f0CookieExpiredCallback:
      oSelf.f0CookieExpiredCallback(oSelf, oCookie, o0PreviousCookie);
  else:
    aoExistingCookies_for_sbLowerDomainName.append(oCookie);
    if oSelf.f0SetCookieCallback:
      oSelf.f0SetCookieCallback(oSelf, oCookie, o0PreviousCookie);
  return oCookie;
