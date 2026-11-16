import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from deploy_ftps import deploy,digest,META,public_permissions
from test_hosting import FTP


class PublicPermissionTests(unittest.TestCase):
    def test_identical_files_still_receive_approved_permissions(self):
        content={'index.html':b'home','categories/hospitals/index.html':b'hospitals'}
        meta={'schema':1,'files':{n:digest(d) for n,d in content.items()}}
        files={**content,META:json.dumps(meta).encode()}
        ftp=FTP({**files,'.htaccess':b'private configuration','mail/private':b'private'})
        before=ftp.files.copy()
        deploy(ftp,files,meta)
        self.assertEqual(ftp.files,before)
        self.assertEqual(ftp.calls,0)
        self.assertEqual(set(ftp.permission_commands),{
            'SITE CHMOD 755 categories','SITE CHMOD 755 categories/hospitals',
            'SITE CHMOD 644 index.html','SITE CHMOD 644 categories/hospitals/index.html',
            'SITE CHMOD 644 '+META})

    def test_invalid_targets_are_rejected_before_any_command(self):
        for target in ['.htaccess','../index.html','mail/private','index.html\r\nDELE other']:
            ftp=FTP()
            with self.assertRaises(ValueError):public_permissions(ftp,{target:b'x'})
            self.assertEqual(ftp.permission_commands,[])

    def test_check_does_not_change_even_public_permissions(self):
        files={'index.html':b'home'}
        meta={'schema':1,'files':{'index.html':digest(b'home')}}
        files[META]=json.dumps(meta).encode()
        ftp=FTP(files)
        deploy(ftp,files,meta,check=True)
        self.assertEqual(ftp.permission_commands,[])


if __name__=='__main__':unittest.main()
