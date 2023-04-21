import functools
from passlib.context import CryptContext

cryptcontext = CryptContext(schemes=["pbkdf2_sha512", "bcrypt", "sha512_crypt", "plaintext"])

def buildHoneyCredHook(creds):
    """
    Return a callable object that can be used as a honeycred_hook in
    OpenCanary's configuration file.

    The callable object will check if a given username and password match
    any of the credentials specified in `creds`.

    Args:
        creds (list of dicts): List of credentials to match against.

    Returns:
        Callable: A function that takes a username and password as arguments
            and returns True if they match any of the credentials in `creds`.

    """
    return functools.partial(testManyCreds, creds)

def testCred(cred, username=None, password=None):
    """
    Test if given credentials match specified credentials.

    If specified credentials do not have a username or password, it
    will still match on the other.

    Args:
        cred (dict): A dictionary representing the credentials to match against.
            It can have the following keys:
                - username: The username to match (optional).
                - password: The password hash to match (optional).
        username (bytes): The username to test (optional).
        password (bytes): The password to test (optional).

    Returns:
        bool: True if the given username and password match the specified credentials.

    """
    cred_username = cred.get("username", None)
    cred_password = cred.get("password", None)

    user_match = True
    if cred_username is not None:
        user_match = (cred_username.encode() == username)

    password_match = True
    if cred_password is not None:
        password_match = cryptcontext.verify(password, cred_password)

    return (user_match and password_match)

def testManyCreds(creds, username=None, password=None):
    """
    Test if given credentials match any of the specified credentials.

    Args:
        creds (list of dicts): List of credentials to match against.
        username (bytes): The username to test (optional).
        password (bytes): The password to test (optional).

    Returns:
        bool: True if the given username and password match any of the credentials.

    """
    for c in creds:
        if testCred(c, username, password):
            return True
    return False
