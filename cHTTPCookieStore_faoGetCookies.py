from mDateTime import cDateTime;

bDebugOutput = False;

def cHTTPCookieStore_faoGetCookies(oSelf):
  oNow = cDateTime.foNow();
  aoCookies = [];
  for aoDomainCookies in oSelf.daoCookies_by_sbLowerDomainName.values():
    for oCookie in aoDomainCookies:
      if (
        oCookie.o0ExpirationDateTime is not None
        and not oCookie.o0ExpirationDateTime.fbIsAfter(oNow)
      ):
        if bDebugOutput: print("| - Cookie expired (%s)" % oCookie);
        continue;
      
      aoCookies.append(oCookie);
  return aoCookies;