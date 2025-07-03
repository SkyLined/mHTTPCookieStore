from mDateTime import cDateTime;

bDebugOutput = False;

def cCookieStore_faoGetCookiesForURL(oSelf, oURL):
  if not oSelf.daoCookies_by_sbLowerDomainName:
    if bDebugOutput: print("| - No cookies in session");
    return [];
  sbLowerHostWithLeadingDot = b".%s" % oURL.sbHost.lower();              # .sub-domain.example.com
  oNow = cDateTime.foNow();
  doCookie_by_sbName = {};
  for (sbLowerDomainName, aoDomainCookies) in oSelf.daoCookies_by_sbLowerDomainName.items():
    # a cookie for "example.com" applies to "example.com" as well as sub-domains of example.com:
    if not sbLowerHostWithLeadingDot.endswith(b".%s" % sbLowerDomainName):
      if bDebugOutput: print("| - URL Host (%s) does not match cookie domain %s" % (
        repr(oURL.sbHost)[1:],
        repr(sbLowerDomainName)[1:],
      ));
      continue;
    
    for oCookie in aoDomainCookies:
      if (
        oCookie.o0ExpirationDateTime is not None
        and not oCookie.o0ExpirationDateTime.fbIsAfter(oNow)
      ):
        if bDebugOutput: print("| - Cookie expired (%s)" % oCookie);
        continue;
      
      if not oCookie.fbAppliesToPath(oURL.sbPath):
        if bDebugOutput: print("| - URL Path (%s) mismatch for cookie %s"  % (
          repr(oURL.sbPath)[1:],
          oCookie,
        ));
        continue;
      
      if oCookie.bSecure and not oURL.bSecure:
        if bDebugOutput: print("| - URL Secure (%s) mismatch for cookie %s" % (
          "yes" if oURL.bSecure else "no",
          oCookie,
        ));
        continue;
      o0OtherCookie = doCookie_by_sbName.get(oCookie.sbName);
      if o0OtherCookie:
        if len(o0OtherCookie.sbDomainName) > len(oCookie.sbDomainName):
          if bDebugOutput: print("| - More specific domain found (%s)" % oCookie);
          continue;
        if bDebugOutput: print("| - More specific domain found (%s)" % o0OtherCookie);
      doCookie_by_sbName[oCookie.sbName] = oCookie;
  aoCookies = doCookie_by_sbName.values();
  if bDebugOutput: 
    for oCookie in aoCookies:
      print("| + Matched cookie %s" % (
        oCookie,
      ));
  return aoCookies;