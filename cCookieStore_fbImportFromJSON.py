import json;

from mDateTime import cDateTime;
from mNotProvided import fbIsProvided, zNotProvided;

from .cCookie import cCookie;

def fxProcessType(sName, xValue, xAcceptedType):
  if not isinstance(xValue, str if xAcceptedType in (bytes, cDateTime) else xAcceptedType):
    raise ValueError(
      "Invalid JSON data: %s (%s) should be of type %s but it is of type %s." % (
        sName, repr(xValue), str(xAcceptedType.__name__), str(xValue.__class__.__name__),
      ),
    );
  if xAcceptedType is bytes:
    try:
      return bytes(xValue, "ascii", "strict");
    except:
      raise ValueError(
        "Invalid JSON data: %s (%s) should be an ASCII string but it is not." % (
          sName, repr(xValue),
        ),
      );
  if xAcceptedType is cDateTime:
    try:
      return cDateTime.foFromString(xValue);
    except:
      raise ValueError(
        "Invalid JSON data: %s (%s) should be an ASCII string containing a date but it is not." % (
          sName, repr(xValue),
        ),
      );
  return xValue;

def cCookieStore_fbImportFromJSON(oSelf, 
  dxJSON,
):
  sMainJSONElementName = "HTTPCookieStore_ddxCookie_by_sName_by_sLowerDomainName";
  if sMainJSONElementName not in dxJSON:
    return False;
  # Process data
  ddxCookie_by_sName_by_sLowerDomainName = fxProcessType(sMainJSONElementName, dxJSON[sMainJSONElementName], dict);
  for (sLowerDomainName, dxCookie_by_sName) in ddxCookie_by_sName_by_sLowerDomainName.items():
    sCookiesForDomainJSONElementName = "%s[%s]" % (sMainJSONElementName, json.dumps(sLowerDomainName));
    sbLowerDomainName = fxProcessType(sCookiesForDomainJSONElementName, sLowerDomainName, bytes);
    oSelf.daoCookies_by_sbLowerDomainName[sbLowerDomainName] = [];
    for (sCookieName, dxCookieProperties) in fxProcessType(sCookiesForDomainJSONElementName, dxCookie_by_sName, dict).items():
      sCookieJSONElementName = "%s[%s]" % (sCookiesForDomainJSONElementName, repr(sCookieName));
      sbCookieName = fxProcessType(sCookieJSONElementName, sCookieName, bytes);
      sbzCookieValue = zNotProvided;
      sbzCookieDomainName = zNotProvided;
      dxCookieAttributeArguments = {};
      for (sCookiePropertyName, xCookiePropertyValue) in fxProcessType(sCookieJSONElementName, dxCookieProperties, dict).items():
        sCookiePropertyJSONElementName = "%s.%s" % (sCookieJSONElementName, sCookiePropertyName);
        if sCookiePropertyName == "sValue":
          sbzCookieValue = fxProcessType(sCookiePropertyJSONElementName, xCookiePropertyValue, bytes);
        elif sCookiePropertyName == "sDomainName":
          sbzCookieDomainName = fxProcessType(sCookiePropertyJSONElementName, xCookiePropertyValue, bytes);
        elif sCookiePropertyName == "sExpirationDateTime":
          dxCookieAttributeArguments["o0ExpirationDateTime"] = fxProcessType(sCookiePropertyJSONElementName, xCookiePropertyValue, cDateTime);
        elif sCookiePropertyName == "sPath":
          dxCookieAttributeArguments["sb0Path"] = fxProcessType(sCookiePropertyJSONElementName, xCookiePropertyValue, bytes);
        elif sCookiePropertyName == "bSecure":
          dxCookieAttributeArguments["bSecure"] = fxProcessType(sCookiePropertyJSONElementName, xCookiePropertyValue, bool);
        elif sCookiePropertyName == "bHttpOnly":
          dxCookieAttributeArguments["bHttpOnly"] = fxProcessType(sCookiePropertyJSONElementName, xCookiePropertyValue, bool);
        elif sCookiePropertyName == "sSameSite":
          dxCookieAttributeArguments["sbSameSite"] = fxProcessType(sCookiePropertyJSONElementName, xCookiePropertyValue, bytes);
        else:
          raise ValueError(
            "Invalid JSON data: %s (%s) is not expected." % (
              sCookiePropertyJSONElementName, repr(xCookiePropertyValue),
            ),
          );
      if not fbIsProvided(sbzCookieValue):
        raise ValueError(
          "Invalid JSON data: Cookie %s properties (%s) is missing a \"sValue\" property." % (
            sCookiePropertyJSONElementName, repr(dxCookieProperties),
          ),
        );
      if not fbIsProvided(sbzCookieDomainName):
        raise ValueError(
          "Invalid JSON data: Cookie %s properties (%s) is missing a \"sDomain\" property." % (
            sCookiePropertyJSONElementName, repr(dxCookieProperties),
          ),
        );
      oCookie = cCookie(sbCookieName, sbzCookieValue, sbzCookieDomainName, **dxCookieAttributeArguments);
      if oCookie.fbIsExpired():
        if oSelf.f0CookieExpiredCallback:
          oSelf.f0CookieExpiredCallback(oSelf, oCookie, None);
      else:
        oSelf.daoCookies_by_sbLowerDomainName[sbLowerDomainName].append(oCookie);
        if oSelf.f0SetCookieCallback:
          oSelf.f0SetCookieCallback(oSelf, oCookie, None);
  return True;
