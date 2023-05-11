import datetime, re;

from mDateTime import cDateTime, cDateTimeDuration;

from .cHTTPCookie import cHTTPCookie;

bDebugOutput = False;

asbWeekNames = [b"Mon", b"Tue", b"Wed", b"Thu", b"Fri", b"Sat", b"Sun"];
asbHTTPMonthNames = [b"Jan", b"Feb", b"Mar", b"Apr", b"May", b"Jun", b"Jul", b"Aug", b"Sep", b"Oct", b"Nov", b"Dec"];
# This is the official format of date/time:
rbHTTPDateTimeFormat_RFC9110 = re.compile(b"".join([
  rb"\A",
  rb"(?:%s)" % rb"|".join(asbWeekNames),    # Day of week name
  rb", ",                                  
  rb"(\d{2})",                              # Day in month
  rb"[ \-]",                               
  rb"(%s)" % b"|".join(asbHTTPMonthNames),  # Month name
  rb"[ \-]",                               
  rb"(\d{4})",                              # Year
  rb" ",                                   
  rb"(\d{2})",                              # Hour
  rb":",                                   
  rb"(\d{2})",                              # Minute
  rb":",                                   
  rb"(\d{2})",                              # Second
  rb" GMT",
  rb"\Z",
]));
# This is also allowed for compatibility with older code.
rbHTTPDateTimeFormat_Compatible = re.compile(b"".join([
  rb"\A",
  rb"(?:%s)" % rb"|".join(asbWeekNames),    # Day of week name (ignored)
  rb"\s+",                                  
  rb"(%s)" % rb"|".join(asbHTTPMonthNames), # Month name
  rb"\s+",                               
  rb"(\d{1,2})",                            # Day in month
  rb"\s+",                               
  rb"(\d{4})",                              # Year
  rb"\s+",                                   
  rb"(\d{1,2})",                            # Hour
  rb":",                                   
  rb"(\d{2})",                              # Minute
  rb":",                                   
  rb"(\d{2})",                              # Second
  rb" GMT",
  rb"(?:\+0+)?",                            # Timezone offset from GMT (must be 0, ignored).
  rb"(?:\s+\(.+\))?",                       # Timezone name (ignored).
  rb"\Z",
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
    bValidExpiresAttributeFound = False;
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
          (sbDay, sbMonthName, sbYear, sbHour, sbMinute, sbSecond) = rbHTTPDateTimeFormat_RFC9110.match(sHTTPDateTime).groups();
        except:
          try:
            (sbMonthName, sbDay, sbYear, sbHour, sbMinute, sbSecond) = rbHTTPDateTimeFormat_Compatible.match(sHTTPDateTime).groups();
          except:
            if bDebugOutput: print("- Invalid 'Expires' attribute for %s" % oHeader);
            if oSelf.f0InvalidCookieAttributeCallback:
              oSelf.f0InvalidCookieAttributeCallback(oSelf, oResponse, oURL, oHeader, sbCookieName, sbCookieValue, sbName, sbValue, True);
            # If the server provides an invalid "Expires" value, we will just ignore it.
            continue;
        oPyExpiresDateTime = datetime.datetime(
          year = int(sbYear),
          month = asbHTTPMonthNames.index(sbMonthName) + 1,
          day = int(sbDay),
          hour = int(sbHour),
          minute = int(sbMinute),
          second = int(sbSecond),
          tzinfo =  datetime.timezone.utc,
        );
        oExpiresDateTime = cDateTime.foFromPyDateTime(oPyExpiresDateTime);
        dxCookieAttributeArguments["o0ExpirationDateTime"] = oExpiresDateTime;
        bValidExpiresAttributeFound = True;
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
          # If the server provides an invalid "Max-Age" value, we will just ignore it.
          continue;
        # Expires header takes precedent. If both are provided, MaxAge is ignored.
        if not bValidExpiresAttributeFound:
          oMaxAgeDateTimeDuration = cDateTimeDuration.fo0FromString("%+ds" % uNumberOfSeconds);
          oExpirationDateTime = cDateTime.foNow().foGetEndDateTimeForDuration(oMaxAgeDateTimeDuration);
          dxCookieAttributeArguments["o0ExpirationDateTime"] = oExpirationDateTime;
      elif sbLowerName == b"domain":
        sbDomainName = sbValue.lstrip(b".");
        sbLowerDomainName = sbDomainName.lower();
        sbLowerURLHostname = oURL.sbHostname.lower();
        if (
          # If the server provides the "Domain" value more than once, the later values are ignored.
          bDomainAttributeFound
          # Cookies with a "__Host-" prefix must *not* have a "Domain" attribute; it will be ignored.
          or bHostPrefix
          or (
            # If the server provides a "Domain" that is not the same as the hostname in the URL
            # or a parent domain, the domain is ignored.
            sbLowerURLHostname != sbLowerDomainName and not sbLowerURLHostname.endswith(b"." + sbLowerDomainName)
          )
        ):
          if bDebugOutput: print("- Invalid 'Domain' attribute for %s" % oHeader);
          if oSelf.f0InvalidCookieAttributeCallback:
            oSelf.f0InvalidCookieAttributeCallback(oSelf, oResponse, oURL, oHeader, sbCookieName, sbCookieValue, sbName, sbValue, True);
        else:
          sbCookieDomainName = sbDomainName;
      elif sbLowerName == b"path":
        # What should we do if the server provides multiple "Path" values?
        # For now we report any later values and ignore them.
        # TODO: find out if there is a standard.
        if "sb0Path" in dxCookieAttributeArguments:
          if oSelf.f0InvalidCookieAttributeCallback:
            oSelf.f0InvalidCookieAttributeCallback(oSelf, oResponse, oURL, oHeader, sbCookieName, sbCookieValue, sbName, sbValue, True);
          continue;
        # Cookies with a "__Host-" prefix *must* have a "Path=/" attribute
        if bHostPrefix and not sbValue == b"/":
          if bDebugOutput: print("- Invalid 'Path' attribute for %s" % oHeader);
          if oSelf.f0InvalidCookieAttributeCallback:
            oSelf.f0InvalidCookieAttributeCallback(oSelf, oResponse, oURL, oHeader, sbCookieName, sbCookieValue, sbName, sbValue, True);
          # The value is ignored and replace with "/"
          dxCookieAttributeArguments["sb0Path"] = b"/";
        else:
          # make sure it starts with a '/' and there is no '/' after the last directory name.
          sbPath = b"/" + sbValue.strip(b"/");
          if not cHTTPCookie.fbIsValidPath(sbPath):
            if bDebugOutput: print("- Invalid 'Path' attribute for %s" % oHeader);
            if oSelf.f0InvalidCookieAttributeCallback:
              oSelf.f0InvalidCookieAttributeCallback(oSelf, oResponse, oURL, oHeader, sbCookieName, sbCookieValue, sbName, sbValue, True);
            sbPath = b"/";
          dxCookieAttributeArguments["sb0Path"] = sbPath;
      elif sbLowerName == b"secure":
        # What should we do if the server provides a value for "Secure"?
        # For now we report and ignore any value. TODO: find out if there is a standard.
        if sbValue:
          if bDebugOutput: print("- Superflous 'Secure' attribute value for %s" % oHeader);
          if oSelf.f0InvalidCookieAttributeCallback:
            oSelf.f0InvalidCookieAttributeCallback(oSelf, oResponse, oURL, oHeader, sbCookieName, sbCookieValue, sbName, sbValue, True);
        dxCookieAttributeArguments["bSecure"] = True;
      elif sbLowerName == b"httponly":
        # What should we do if the server provides a value for "HttpOnly"?
        # For now we report and ignore any value. TODO: find out if there is a standard.
        if sbValue:
          if bDebugOutput: print("- Superflous 'HttpOnly' attribute value for %s" % oHeader);
          if oSelf.f0InvalidCookieAttributeCallback:
            oSelf.f0InvalidCookieAttributeCallback(oSelf, oResponse, oURL, oHeader, sbCookieName, sbCookieValue, sbName, sbValue, True);
        dxCookieAttributeArguments["bHttpOnly"] = True;
      elif sbLowerName == b"samesite":
        if not sbValue:
          if bDebugOutput: print("- Missing 'SameSite' attribute value for %s" % oHeader);
          if oSelf.f0InvalidCookieAttributeCallback:
            oSelf.f0InvalidCookieAttributeCallback(oSelf, oResponse, oURL, oHeader, sbCookieName, sbCookieValue, sbName, sbValue, True);
          dxCookieAttributeArguments["sbSameSite"] = b"Lax"; # The default
        else:
          # Fix casing if needed.
          sbCapitalizedValue = sbValue[:1].upper() + sbValue[1:].lower();
          if sbCapitalizedValue in (b"Strict", b"Lax", b"None"):
            dxCookieAttributeArguments["sbSameSite"] = sbCapitalizedValue;
          else:
            # What should we do if the client provides an invalid "SameSite" value?
            if bDebugOutput: print("- Invalid 'SameSite' attribute for %s" % oHeader);
            # For now we report use the default "Lax" value. TODO: find out if there is a standard.
            if oSelf.f0InvalidCookieAttributeCallback:
              oSelf.f0InvalidCookieAttributeCallback(oSelf, oResponse, oURL, oHeader, sbCookieName, sbCookieValue, sbName, sbValue, True);
            dxCookieAttributeArguments["sbSameSite"] = b"Lax"; # The default
      else:
        # What should we do if the server provides an unhandled named value?
        # For now we report and ignore any value. TODO: find out if there is a standard.
        if bDebugOutput: print("- Unknown %s attribute for cookie %s" % (repr(sbName), repr(sbCookieName)));
        if oSelf.f0InvalidCookieAttributeCallback:
          oSelf.f0InvalidCookieAttributeCallback(oSelf, oResponse, oURL, oHeader, sbCookieName, sbCookieValue, sbName, sbValue, False);
    if bSecurePrefix or bHostPrefix:
      # Cookies with these two prefixes MUST have the "Secure" attribute set.
      if not dxCookieAttributeArguments.get("bSecure"):
        if bDebugOutput: print("- Missing 'Secure' attribute for %s" % oHeader);
        if oSelf.f0InvalidCookieAttributeCallback:
          oSelf.f0InvalidCookieAttributeCallback(oSelf, oResponse, oURL, oHeader, sbCookieName, sbCookieValue, "Secure", None, False);
        dxCookieAttributeArguments["bSecure"] = True;
      # Cookies with a "__Host-" prefix MUST have the "Path" attribute set (to "/", but we checked for that earlier).
      if bHostPrefix and not "sb0Path" in dxCookieAttributeArguments:
        if bDebugOutput: print("- Missing 'Path' attribute for %s" % oHeader);
        if oSelf.f0InvalidCookieAttributeCallback:
          oSelf.f0InvalidCookieAttributeCallback(oSelf, oResponse, oURL, oHeader, sbCookieName, sbCookieValue, "Path", dxCookieAttributeArguments.get("sb0Path"), False);
        dxCookieAttributeArguments["sb0Path"] = b"/";
    oCookie = oSelf.foAddCookie(
      sbCookieName,
      sbCookieValue,
      sbCookieDomainName,
      **dxCookieAttributeArguments,
    );
    if oSelf.f0CookieReceivedCallback:
      oSelf.f0CookieReceivedCallback(oSelf, oResponse, oURL, oCookie);
    if bDebugOutput: print("+ Added cookie %s" % oCookie);
