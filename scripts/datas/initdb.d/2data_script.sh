#!/bin/bash

echo "Adding Groups"
ldapadd -D "cn=Directory Manager" -w ${DS_DM_PASSWORD} -H ldap://localhost:3389 -x <<EOF
dn: cn=UAFS_ADMINS,cn=Groups,cn=Person,${DS_SUFFIX_NAME}
cn: UAFS_ADMINS
objectclass: groupOfNames
EOF

ldapadd -D "cn=Directory Manager" -w ${DS_DM_PASSWORD} -H ldap://localhost:3389 -x <<EOF
dn: cn=UAFS_ADVISORS,cn=Groups,cn=Person,${DS_SUFFIX_NAME}
cn: UAFS_ADVISORS
objectclass: groupOfNames
EOF

ldapadd -D "cn=Directory Manager" -w ${DS_DM_PASSWORD} -H ldap://localhost:3389 -x <<EOF
dn: cn=UAFS_STUDENTS,cn=Groups,cn=Person,${DS_SUFFIX_NAME}
cn: UAFS_STUDENTS
objectclass: groupOfNames
EOF



echo "Adding Users"

# ---------- Admins ----------
ldapadd -D "cn=Directory Manager" -w ${DS_DM_PASSWORD} -H ldap://localhost:3389 -x <<EOF
dn: uid=aapply00@uafs.edu,cn=Users,cn=Person,${DS_SUFFIX_NAME}
uid: aapply00@uafs.edu
givenName: Andrew
sn: Andrew
cn: Andrew Admin
objectClass: inetorgperson
objectClass: inetuser
userPassword: password123
EOF

# ldapadd -D "cn=Directory Manager" -w ${DS_DM_PASSWORD} -H ldap://localhost:3389 -x <<EOF
# dn: uid=admin@uafs.edu,cn=Users,cn=Person,${DS_SUFFIX_NAME}
# uid: admin@uafs.edu
# givenName: Bob
# sn: Admin
# cn: Bob Admin
# objectClass: inetorgperson
# objectClass: inetuser
# userPassword: password123
# EOF

ldapadd -D "cn=Directory Manager" -w ${DS_DM_PASSWORD} -H ldap://localhost:3389 -x <<EOF
dn: uid=amackey00@uafs.edu,cn=Users,cn=Person,${DS_SUFFIX_NAME}
uid: amackey00@uafs.edu
givenName: Andrew
sn: Advisor
cn: Andrew Advisor
objectClass: inetorgperson
objectClass: inetuser
userPassword: password123
EOF

ldapadd -D "cn=Directory Manager" -w ${DS_DM_PASSWORD} -H ldap://localhost:3389 -x <<EOF
dn: uid=icuevas00@uafs.edu,cn=Users,cn=Person,${DS_SUFFIX_NAME}
uid: icuevas00@uafs.edu
givenName: Israel
sn: Advisor
cn: Israel Advisor
objectClass: inetorgperson
objectClass: inetuser
userPassword: password123
EOF

ldapadd -D "cn=Directory Manager" -w ${DS_DM_PASSWORD} -H ldap://localhost:3389 -x <<EOF
dn: uid=bbright@uafs.edu,cn=Users,cn=Person,${DS_SUFFIX_NAME}
uid: bbright00@uafs.edu
givenName: Brittany
sn: Advisor
cn: Brittany Advisor
objectClass: inetorgperson
objectClass: inetuser
userPassword: password123
EOF

ldapadd -D "cn=Directory Manager" -w ${DS_DM_PASSWORD} -H ldap://localhost:3389 -x <<EOF
dn: uid=ypatel00@uafs.edu,cn=Users,cn=Person,${DS_SUFFIX_NAME}
uid: ypate00@uafs.edu
givenName: Yash
sn: Student
cn: Yash Student
objectClass: inetorgperson
objectClass: inetuser
userPassword: password123
EOF

ldapadd -D "cn=Directory Manager" -w ${DS_DM_PASSWORD} -H ldap://localhost:3389 -x <<EOF
dn: uid=cmonte00@uafs.edu,cn=Users,cn=Person,${DS_SUFFIX_NAME}
uid: cmonte00@uafs.edu
givenName: Christopher
sn: Student
cn: Christopher Student
objectClass: inetorgperson
objectClass: inetuser
userPassword: password123
EOF

ldapadd -D "cn=Directory Manager" -w ${DS_DM_PASSWORD} -H ldap://localhost:3389 -x <<EOF
dn: uid=rfarra00@uafs.edu,cn=Users,cn=Person,${DS_SUFFIX_NAME}
uid: rfarra00@uafs.edu
givenName: Robert
sn: Student
cn: Robert Student
objectClass: inetorgperson
objectClass: inetuser
userPassword: password123
EOF

ldapadd -D "cn=Directory Manager" -w ${DS_DM_PASSWORD} -H ldap://localhost:3389 -x <<EOF
dn: uid=jake00@uafs.edu,cn=Users,cn=Person,${DS_SUFFIX_NAME}
uid: jake00@uafs.edu
givenName: Jake
sn: Student
cn: Jake Student
objectClass: inetorgperson
objectClass: inetuser
userPassword: password123
EOF


echo "addings Users to group"
# Add Admins to UAFS_ADMINS
ldapmodify -D "cn=Directory Manager" -w ${DS_DM_PASSWORD} -H ldap://localhost:3389 -x <<EOF
dn: cn=UAFS_ADMINS,cn=Groups,cn=Person,${DS_SUFFIX_NAME}
changetype: modify
add: member
member: uid=aapply00@uafs.edu,cn=Users,cn=Person,${DS_SUFFIX_NAME}
EOF

# Add Advisors to UAFS_ADVISORS
ldapmodify -D "cn=Directory Manager" -w ${DS_DM_PASSWORD} -H ldap://localhost:3389 -x <<EOF
dn: cn=UAFS_ADVISORS,cn=Groups,cn=Person,${DS_SUFFIX_NAME}
changetype: modify
add: member
member: uid=amackey00@uafs.edu,cn=Users,cn=Person,${DS_SUFFIX_NAME}
member: uid=icuevas00@uafs.edu,cn=Users,cn=Person,${DS_SUFFIX_NAME}
member: uid=bbright00@uafs.edu,cn=Users,cn=Person,${DS_SUFFIX_NAME}
EOF

# Add Students to UAFS_STUDENTS
ldapmodify -D "cn=Directory Manager" -w ${DS_DM_PASSWORD} -H ldap://localhost:3389 -x <<EOF
dn: cn=UAFS_STUDENTS,cn=Groups,cn=Person,${DS_SUFFIX_NAME}
changetype: modify
add: member
member: uid=ypatel00@uafs.edu,cn=Users,cn=Person,${DS_SUFFIX_NAME}
member: uid=cmonte00@uafs.edu,cn=Users,cn=Person,${DS_SUFFIX_NAME}
member: uid=rfarra00@uafs.edu,cn=Users,cn=Person,${DS_SUFFIX_NAME}
member: uid=jake00@uafs.edu,cn=Users,cn=Person,${DS_SUFFIX_NAME}
EOF