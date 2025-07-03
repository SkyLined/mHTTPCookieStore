from .cCookie import cCookie;

def cCookieStore_fbRemoveCookie(oSelf, oCookie):
  sbLowerCookieDomainName = oCookie.sbDomainName.lower();
  aoExistingCookies_for_sbLowerDomainName = oSelf.daoCookies_by_sbLowerDomainName.setdefault(sbLowerCookieDomainName, []);
  if oCookie in aoExistingCookies_for_sbLowerDomainName:
    aoExistingCookies_for_sbLowerDomainName.remove(oCookie);
    return True;
  return False;
