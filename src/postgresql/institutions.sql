CREATE TABLE institutions (
    nsid TEXT PRIMARY KEY,
    name TEXT,
    date_launch BIGINT,
    website TEXT,
    license TEXT,
    flickr_page TEXT
);

-- example insert
INSERT INTO institutions (nsid, name, date_launch, website, license, flickr_page)
VALUES (
    '203653061@N02',
    'Eötvös Loránd University Faculty of Law Library',
    1760634342,
    'https://konyvtar.ajk.elte.hu',
    'https://www.flickr.com/people/eltelawlibrary/',
    'http://flickr.com/photos/eltelawlibrary/'
);

-- example access data
SELECT * FROM institutions WHERE nsid = '203653061@N02';
