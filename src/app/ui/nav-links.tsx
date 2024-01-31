'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import clsx from 'clsx';


const links = [
    { name: '/home', href: '/'},
    { name: '/bin/shop', href: '/shop'},
    { name: '/bin/whoami', href: '/about'},
    { name: '/var/log', href: '/log'},
    { name: '/etc/en', href: '/en'},
];

export default function NavLinks() {
    const pathname = usePathname();
    return (
        <>
            {links.map((link) => {
                return (
                    <Link
                        key={link.name}
                        href={link.href}
                        className={clsx('hover:bg-white hover:text-black',
                            {
                                'bg-white text-black': pathname === link.href,	
                            },
                        )}
                    >
                        {link.name}
                    </Link>
                );
            })}
        </>
    );
}