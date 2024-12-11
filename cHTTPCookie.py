import re;

from mDateTime import cDateTime;
from mNotProvided import fAssertTypes;

from .mExceptions import (
  cInvalidCookieDomainNameException,
  cInvalidCookieSameSiteException,
  cInvalidCookiePathException,
);


rDomainNameFormat = re.compile(
  rb"\A"
  rb"\.?" # a single leading '.' is allowed but ignored.
  rb"(?:[a-z0-9_\-]+\.)*" # optional several sub-domains + '.'
  rb"[a-z0-9_\-]+"      # TLD if sub-domains are provided, or hostname if they are not.
  rb"\Z"
);
rPathFormat = re.compile(
  # I do not know how to handle missing leading slashes, superfluous trailing slashes, "//", "/.", or "/..".
  # I've implemented it to allow missing leading slashes and superfluous trailing slashes, not allow "//", and to
  # tread "/." and "/.." as the names of folders, rather than implement directory traversal.
  rb"\A"
  rb"\/?"               # optionally start with '/'
  rb"(?:[^\/\?#]+\/)*"  # optional { several folder names + '/' }
  rb"(?:[^\/\?#]+\/?)?" # optional { folder name + optional '/' }
  rb"\Z"
);

class cHTTPCookie(object):
  @staticmethod
  def fbIsValidDomainName(sbDomainName):
    return rDomainNameFormat.match(sbDomainName.lstrip(b".")) is not None;
  @staticmethod
  def fbIsValidPath(sbPath):
    return rPathFormat.match(sbPath) is not None;

  @classmethod
  def foFromNetscapeFileFormat(cClass, sbLine):
    asbLine = sbLine.split(b"\t");
    if len(asbLine) != 7:
      raise ValueError("Cookie does not adhere to Netscape File Format: %s" % repr(sbLine)[1:]);
    (
      sbHttpOnlyAndDomainName,
      sbIncludeSubdomain,
      sbPath,
      sbSecure,
      sbExpirationTimestamp,
      sbName,
      sbValue,
    ) = asbLine;
    bHttpOnly = sbHttpOnlyAndDomainName.startswith(b"#HttpOnly_");
    
    sbDomainName = sbHttpOnlyAndDomainName[len(b"#HttpOnly_"):] if bHttpOnly else sbHttpOnlyAndDomainName;
    if not cClass.fbIsValidDomainName(sbDomainName):
      raise ValueError("Cookie does not adhere to Netscape File Format (domain name == %s is invalid): %s" % (repr(sbDomainName), repr(sbLine)[1:]));
    
    b0IncludeSubdomain = {b"TRUE": True, b"FALSE": False}.get(sbIncludeSubdomain);
    if b0IncludeSubdomain is None:
      raise ValueError("Cookie does not adhere to Netscape File Format (include subdomain == %s is invalid): %s" % (repr(sbIncludeSubdomain), repr(sbLine)[1:]));
    
    if not cClass.fbIsValidPath(sbPath):
      raise ValueError("Cookie does not adhere to Netscape File Format (path == %s is invalid): %s" % (repr(sbPath), repr(sbLine)[1:]));
    
    b0Secure = {b"TRUE": True, b"FALSE": False}.get(sbSecure);
    if b0Secure is None:
      raise ValueError("Cookie does not adhere to Netscape File Format (secure == %s is invalid): %s" % (repr(sbSecure), repr(sbLine)[1:]));
    
    try:
      uExpirationTimestamp = int(sbExpirationTimestamp);
    except:
      raise ValueError("Cookie does not adhere to Netscape File Format (expiration timestamp == %s is invalid): %s" % (repr(sbExpirationTimestamp), repr(sbLine)[1:]));
    o0ExpirationDateTime = cDateTime.foFromTimestamp(uExpirationTimestamp);
    
    return cClass(
      sbName,
      sbValue,
      sbDomainName,
      o0ExpirationDateTime = o0ExpirationDateTime,
      sb0Path = sbPath,
      bSecure = b0Secure,
      bHttpOnly = bHttpOnly,
    );

  def __init__(oSelf,
    sbName,
    sbValue,
    sbDomainName,
    *,
    o0ExpirationDateTime = None,
    sb0Path = None,
    bSecure = False,
    bHttpOnly = False,
    sbSameSite = b"Lax",
  ):
    fAssertTypes({
      "sbName": (sbName, bytes),
      "sbValue": (sbValue, bytes),
      "sbDomainName": (sbDomainName, bytes),
      "o0ExpirationDateTime": (o0ExpirationDateTime, cDateTime, None),
      "sb0Path": (sb0Path, bytes, None),
      "bSecure": (bSecure, bool),
      "bHttpOnly": (bHttpOnly, bool),
      "sbSameSite": (sbSameSite, bytes),
    });
    oSelf.sbName = sbName;
    oSelf.sbValue = sbValue;
    oSelf.o0ExpirationDateTime = o0ExpirationDateTime;
    oSelf.__sbDomainName = sbDomainName.lstrip(b".");
    oSelf.__sb0Path = sb0Path;
    oSelf.bSecure = bSecure;
    oSelf.bHttpOnly = bHttpOnly;
    oSelf.__sbSameSite = sbSameSite;
    # Validity check after setting everything up:
    oSelf.sbDomainName = sbDomainName; # triggers an exception if invalid.
    oSelf.sbSameSite = sbSameSite; # triggers an exception if invalid.
    oSelf.sb0Path = sb0Path; # triggers an exception if invalid.
  
  @property
  def sbDomainName(oSelf):
    return oSelf.__sbDomainName;
  @sbDomainName.setter
  def sbDomainName(oSelf, sbDomainName):
    oSelf.__sbDomainName = sbDomainName;
    if not oSelf.fbIsValidDomainName(sbDomainName):
      raise cInvalidCookieDomainNameException(
        "sbDomainName must be None or a valid domain name, not %s" % repr(sbDomainName),
        oSelf,
      );
  
  @property
  def sbSameSite(oSelf):
    return oSelf.__sbSameSite;
  @sbSameSite.setter
  def sbSameSite(oSelf, sbSameSite):
    oSelf.__sbSameSite = sbSameSite;
    if not sbSameSite in [b"Strict", b"Lax", b"None"]:
      raise cInvalidCookieSameSiteException(
        "sbSameSite must be \"Strict\",  \"Lax\", or \"None\", not %s" % repr(sbSameSite),
        oSelf,
      );
  
  @property
  def sb0Path(oSelf):
    return oSelf.__sb0Path;
  @sb0Path.setter
  def sb0Path(oSelf, sb0Path):
    oSelf.__sb0Path = sb0Path;
    if sb0Path is not None and not oSelf.fbIsValidPath(sb0Path):
      raise cInvalidCookiePathException(
        "sb0Path must be None or a valid path, not %s" % repr(sb0Path),
        oSelf,
      );
  
  def fbAppliesToDomainName(oSelf, sbDomainName):
    sbLowerCookieDomainNameWithLeadingDot = b".%s" % oSelf.sbDomainName.lstrip(b".").lower();
    sbLowerDomainNameWithLeadingDot = b".%s" % sbDomainName.lower();
    if not sbLowerDomainNameWithLeadingDot.endswith(sbLowerCookieDomainNameWithLeadingDot):
      return False;
    return True;
  
  def fbAppliesToPath(oSelf, sbPath):
    # I do not know if this match is case sensitive or not. I've implemented it case insensitive.
    if oSelf.__sb0Path is None:
      return True; # Applies to all paths.
    sbLowerCookiePathWithLeadingAndTrailingSlash = b"/%s/" % oSelf.__sb0Path.strip(b"/").lower();
    if sbLowerCookiePathWithLeadingAndTrailingSlash == b"//":
      sbLowerCookiePathWithLeadingAndTrailingSlash = b"/";
    sbLowerPathWithLeadingAndTrailingSlash = b"/%s/" % sbPath.strip(b"/").lower();
    if sbLowerPathWithLeadingAndTrailingSlash == b"//":
      sbLowerPathWithLeadingAndTrailingSlash = b"/";
    if not sbLowerPathWithLeadingAndTrailingSlash.startswith(sbLowerCookiePathWithLeadingAndTrailingSlash):
      return False; # different path altogether
    return True;
  
  def fbIsSessionCookie(oSelf):
    return oSelf.o0ExpirationDateTime is None;
  
  def fbIsExpired(oSelf):
    if oSelf.o0ExpirationDateTime is None:
      return False;
    return oSelf.o0ExpirationDateTime.fbIsBefore(cDateTime.foNow());
  
  def __str__(oSelf):
    asDetails = [
      "%s=%s" % (repr(oSelf.sbName)[1:], repr(oSelf.sbValue)[1:]),
      "Domain name = %s" % repr(oSelf.__sbDomainName)[1:],
    ];
    if oSelf.o0ExpirationDateTime is not None:
      oValidDuration = cDateTime.foNow().foGetDurationForEndDateTime(oSelf.o0ExpirationDateTime);
      oValidDuration.fNormalize();
      if oSelf.fbIsExpired():
        asDetails.append("Expired %s ago" % oValidDuration.fsToHumanReadableString(u0MaxNumberOfUnitsInOutput = 2));
      else:
        asDetails.append("Expires in %s" % oValidDuration.fsToHumanReadableString(u0MaxNumberOfUnitsInOutput = 2));
    if oSelf.__sb0Path is not None:
      asDetails.append("Path = %s" % repr(oSelf.__sb0Path)[1:]);
    if oSelf.bSecure:
      asDetails.append("Secure");
    if oSelf.bHttpOnly:
      asDetails.append("HttpOnly");
    if oSelf.__sbSameSite != "Lax":
      asDetails.append("SameSite = %s" % repr(oSelf.__sbSameSite)[1:]);
    return "; ".join(asDetails);
  
  def fsbToNetscapeFileFormat(oSelf):
    return b" ".join([
      "%s%s" % (
        b"#HttpOnly_." if oSelf.bHtttpOnly else b"",
        oSelf.__sbDomainName.lstrip(b"."),
      ),
      b"FALSE",
      oSelf.__sb0Path or b"/",
      b"TRUE" if oSelf.bSecure else b"FALSE",
      oSelf.o0ExpirationDateTime.fuToTimestamp() if oSelf.o0ExpirationDateTime else 0,
      oSelf.sbName,
      oSelf.sbValue,
    ]);

  def __repr__(oSelf):
    return "<%s.%s %s>" % (
      oSelf.__class__.__module__,
      oSelf.__class__.__name__,
      str(oSelf),
    );