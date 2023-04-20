def cHTTPCookieStore_fdxExportToJSON(oSelf):
  # Create Cookies JSON data:
  ddxCookie_by_sName_by_sLowerDomainName = {};
  for (sbLowerDomainName, aoCookies) in oSelf.daoCookies_by_sbLowerDomainName.items():
    sLowerDomainName = str(sbLowerDomainName, "ascii", "strict");
    ddxCookie_by_sName_by_sLowerDomainName[sLowerDomainName] = {};
    for oCookie in aoCookies:
      sName = str(oCookie.sbName, "ascii", "strict");
      dxCookie = {
        "sValue": str(oCookie.sbValue, "ascii", "strict"),
        "sDomainName": str(oCookie.sbDomainName, "ascii", "strict"),
      };
      if oCookie.o0ExpirationDateTime is not None:
        dxCookie["sExpirationDateTime"] = oCookie.o0ExpirationDateTime.fsToString();
      if oCookie.sb0Path is not None:
        dxCookie["sPath"] = str(oCookie.sb0Path, "ascii", "strict");
      if oCookie.bSecure:
        dxCookie["bSecure"] = True;
      if oCookie.bHttpOnly:
        dxCookie["bHttpOnly"] = True;
      if oCookie.sbSameSite != b"Lax":
        dxCookie["sSameSite"] = str(oCookie.sbSameSite, "ascii", "strict");
      ddxCookie_by_sName_by_sLowerDomainName[sLowerDomainName][sName] = dxCookie;
  # Create Session JSON data; only add properties that are non-default:
  dxJSON = {
    "HTTPCookieStore_ddxCookie_by_sName_by_sLowerDomainName": ddxCookie_by_sName_by_sLowerDomainName,
  };
  return dxJSON;
