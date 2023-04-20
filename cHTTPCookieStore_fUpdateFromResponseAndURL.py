import datetime, re;

from mDateTime import cDateTime, cDateTimeDuration;

from .cHTTPCookie import cHTTPCookie;

bDebugOutput = False;

asHTTPMonthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
rHTTPDateTimeFormat = re.compile("".join([
  r"\A",
  r"(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)",       # Day of week name
  r", ",                                  
  r"(\d{2})",                             # Day in month
  r"[ \-]",                               
  r"(%s)" % "|".join(asHTTPMonthNames),   # Month name
  r"[ \-]",                               
  r"(\d{4})",                             # Year
  r" ",                                   
  r"(\d{2})",                             # Hour
  r":",                                   
  r"(\d{2})",                             # Minute
  r":",                                   
  r"(\d{2})",                             # Second
  r" GMT",
  r"\Z",
]));

def cHTTPCookieStore_fUpdateFromResponseAndURL(oSelf,
  oResponse,
  oURL,
):
  # Update the cookies provided in the response:
  for oHeader in oResponse.oHeaders.faoGetHeadersForName(b"Set-Cookie"):
    aCookie_tsbName_and_sbValue = oHeader.fGet_atsbName_and_sbValue();
    # The first name-value pair is the cookie's name and value.
    sbCookieName, sbCookieValue = aCookie_tsbName_and_sbValue.pop(0);
    sbCookieDomainName = oURL.sbHostname;
    sbLowerCookieDomainName = sbCookieDomainName.lower()
    # Go through any remaining name-value pairs and handle them as cookie attributes. 
    bExpiresAttributeFound = False;
    bDomainAttributeFound = False;
    dxCookieAttributeArguments = {};
    bSecurePrefix = sbCookieName.startswith(b"__Secure-");
    bHostPrefix = sbCookieName.startswith(b"__Host-");
    for (sbName, sbValue) in aCookie_tsbName_and_sbValue:
      sbLowerName = sbName.lower();
      if sbLowerName == b"expires":
        # What should we do if the server provides multiple "Expires" values?
        # For now we use the last valid value. TODO: find out if there is a standard.
        sHTTPDateTime = str(sbValue, "ascii", "strict");
        try:
          (sDay, sMonthName, sYear, sHour, sMinute, sSecond) = rHTTPDateTimeFormat.match(sHTTPDateTime).groups();
        except:
          if bDebugOutput: print("- Invalid 'Expires' attribute for %s" % oHeader);
          if oSelf.f0InvalidCookieAttributeCallback:
            oSelf.f0InvalidCookieAttributeCallback(oSelf, oResponse, oURL, oHeader, sbCookieName, sbCookieValue, sbName, sbValue, True);
          # If the server provides an invalid "Expires" value, the cookie is ignored.
          break;
        else:
          oPyExpiresDateTime = datetime.datetime(
            year = int(sYear),
            month = asHTTPMonthNames.index(sMonthName) + 1,
            day = int(sDay),
            hour = int(sHour),
            minute = int(sMinute),
            second = int(sSecond),
            tzinfo =  datetime.timezone.utc,
          );
          oExpiresDateTime = cDateTime.foFromPyDateTime(oPyExpiresDateTime);
          dxCookieAttributeArguments["o0ExpirationDateTime"] = oExpiresDateTime;
          bExpiresAttributeFound = True;
      elif sbLowerName == b"max-age":
        # What should we do if the server provides multiple "Max-Age" values?
        # For now we use the last valid value. TODO: find out if there is a standard.
        try:
          uNumberOfSeconds = int(sbValue);
          if uNumberOfSeconds < 0:
            raise ValueError();
        except ValueError:
          if bDebugOutput: print("- Invalid 'Max-Age' attribute for %s" % oHeader);
          if oSelf.f0InvalidCookieAttributeCallback:
            oSelf.f0InvalidCookieAttributeCallback(oSelf, oResponse, oURL, oHeader, sbCookieName, sbCookieValue, sbName, sbValue, True);
          # If the server provides an invalid "Max-Age" value, the cookie is ignored.
          break;
        else:
          # expires header takes precedent.
          if not bExpiresAttributeFound:
            oMaxAgeDateTimeDuration = cDateTimeDuration.fo0FromString("%+ds" % uNumberOfSeconds);
            oExpirationDateTime = cDateTime.foNow().foGetEndDateTimeForDuration(oMaxAgeDateTimeDuration);
            dxCookieAttributeArguments["o0ExpirationDateTime"] = oExpirationDateTime;
      elif sbLowerName == b"domain":
        sbCookieDomainName = sbValue.lstrip(b".");
        sbLowerCookieDomainName = sbCookieDomainName.lower();
        sbLowerURLHostname = oURL.sbHostname.lower();
        if (
          # If the server provides the "Domain" value more than once, the cookie is ignored.
          bDomainAttributeFound
          # Cookies with a "__Host-" prefix must *not* have a "Domain" attribute
          or bHostPrefix
          or (
            # If the server provides a "Domain" that is not the same as the hostname in the URL or a parent domain:
            sbLowerURLHostname != sbLowerCookieDomainName and not sbLowerURLHostname.endswith(b"." + sbLowerCookieDomainName)
          )
        ):
          if bDebugOutput: print("- Invalid 'Domain' attribute for %s" % oHeader);
          if oSelf.f0InvalidCookieAttributeCallback:
            oSelf.f0InvalidCookieAttributeCallback(oSelf, oResponse, oURL, oHeader, sbCookieName, sbCookieValue, sbName, sbValue, True);
          break;
      elif sbLowerName == b"path":
        # Cookies with a "__Host-" prefix *must* have a "Path=/" attribute
        if bHostPrefix and not sbValue == b"/":
          if bDebugOutput: print("- Invalid 'Path' attribute for %s" % oHeader);
          if oSelf.f0InvalidCookieAttributeCallback:
            oSelf.f0InvalidCookieAttributeCallback(oSelf, oResponse, oURL, oHeader, sbCookieName, sbCookieValue, "Secure", None, False);
          break;
        # What should we do if the server provides multiple "Path" values?
        # For now we use the last valid value. TODO: find out if there is a standard.
        # make sure it starts with a '/' and there is no '/' after the last directory name).
        sbPath = b"/" + sbValue.strip(b"/");
        if not cHTTPCookie.fbIsValidPath(sbPath):
          if bDebugOutput: print("- Invalid 'Path' attribute for %s" % oHeader);
          if oSelf.f0InvalidCookieAttributeCallback:
            oSelf.f0InvalidCookieAttributeCallback(oSelf, oResponse, oURL, oHeader, sbCookieName, sbCookieValue, sbName, sbValue, True);
          break;
        dxCookieAttributeArguments["sb0Path"] = sbPath;
      elif sbLowerName == b"secure":
        # What should we do if the server provides a value for "Secure"?
        # For now we ignore any value. TODO: find out if there is a standard.
        dxCookieAttributeArguments["bSecure"] = True;
      elif sbLowerName == b"httponly":
        # What should we do if the server provides a value for "HttpOnly"?
        # For now we ignore any value. TODO: find out if there is a standard.
        dxCookieAttributeArguments["bHttpOnly"] = True;
      elif sbLowerName == b"samesite":
        # Fix casing if needed.
        sbCapitalizedValue = sbValue[:1].upper() + sbValue[1:].lower();
        if sbCapitalizedValue in (b"Strict", b"Lax", b"None"):
          dxCookieAttributeArguments["sbSameSite"] = sbCapitalizedValue;
        else:
          # What should we do if the client provides an invalid "SameSite" value?
          if bDebugOutput: print("- Invalid 'SameSite' attribute for %s" % oHeader);
          if oSelf.f0InvalidCookieAttributeCallback:
            oSelf.f0InvalidCookieAttributeCallback(oSelf, oResponse, oURL, oHeader, sbCookieName, sbCookieValue, sbName, sbValue, True);
          break;
      else:
        # What should we do if the server provides an unhandled named value?
        if bDebugOutput: print("- Unknown %s attribute for cookie %s" % (repr(sbName), repr(sbCookieName)));
        if oSelf.f0InvalidCookieAttributeCallback:
          oSelf.f0InvalidCookieAttributeCallback(oSelf, oResponse, oURL, oHeader, sbCookieName, sbCookieValue, sbName, sbValue, False);
        break;
    # An invalid Set-Cookie header will "break" the loop. "else" here makes sure we only
    # accept the cookie if it's valid:
    else:
      if bSecurePrefix or bHostPrefix:
        # Cookies with these two prefixes MUST have the "Secure" attribute set.
        if not dxCookieAttributeArguments.get("bSecure"):
          if bDebugOutput: print("- Missing 'Secure' attribute for %s" % oHeader);
          if oSelf.f0InvalidCookieAttributeCallback:
            oSelf.f0InvalidCookieAttributeCallback(oSelf, oResponse, oURL, oHeader, sbCookieName, sbCookieValue, "Secure", None, False);
          continue;
        # Cookies with a "__Host-" prefix MUST have the "Path" attribute set (to "/", but we checked for that earlier).
        if bHostPrefix and not "sb0Path" in dxCookieAttributeArguments:
          if bDebugOutput: print("- Missing 'Path' attribute for %s" % oHeader);
          if oSelf.f0InvalidCookieAttributeCallback:
            oSelf.f0InvalidCookieAttributeCallback(oSelf, oResponse, oURL, oHeader, sbCookieName, sbCookieValue, "Path", dxCookieAttributeArguments.get("sb0Path"), False);
          break;
      oCookie = oSelf.foAddCookie(
        sbCookieName,
        sbCookieValue,
        sbCookieDomainName,
        **dxCookieAttributeArguments,
      );
      if oSelf.f0CookieReceivedCallback:
        oSelf.f0CookieReceivedCallback(oSelf, oResponse, oURL, oCookie);
      if bDebugOutput: print("+ Added cookie %s" % oCookie);
