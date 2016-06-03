/*
:date: 16/06/2015
:author: al
*/
alter table abe_group_gm drop foreign key gms_of_gc;
alter table abe_attribute drop foreign key attributes_of_gc;
alter table attribute_to_gm drop foreign key attribute_to_gms;
alter table attribute_to_gm drop foreign key attributes_to_gm;
drop table if exists abe_group_gc;
drop table if exists abe_group_gm;
drop table if exists abe_attribute;
drop table if exists attribute_to_gm;
create table abe_group_gc (id int(10) not null auto_increment, name varchar(255), pk text, mk text, dek varchar(255), date_dek_created datetime null, conversion_factor bigint(20), mqtt_topic varchar(333), abe_type varchar(255), abe_curve varchar(255), primary key (id)) ENGINE=InnoDB CHARACTER SET UTF8;
create table abe_group_gm (id int(10) not null auto_increment, gc_id int(10) not null, name varchar(255), mqtt_topic varchar(333), gm_key varchar(255), sk text, dek varchar(255), sn_access_structure text, sn_pk int(10), sn_abe_type varchar(255), sn_abe_curve varchar(255), primary key (id), index (gm_key)) ENGINE=InnoDB CHARACTER SET UTF8;
create table abe_attribute (id int(10) not null auto_increment, value varchar(255), gc_id int(10) not null, primary key (id), index (gc_id)) ENGINE=InnoDB CHARACTER SET UTF8;
create table attribute_to_gm (attribute_id int(10) not null, gm_id int(10) not null, primary key (attribute_id, gm_id)) ENGINE=InnoDB CHARACTER SET UTF8;
alter table abe_group_gm add index gms_of_gc (gc_id), add constraint gms_of_gc foreign key (gc_id) references abe_group_gc (id) on delete Cascade;
alter table abe_attribute add index attributes_of_gc (gc_id), add constraint attributes_of_gc foreign key (gc_id) references abe_group_gc (id) on delete Cascade;
alter table attribute_to_gm add index attribute_to_gms (attribute_id), add constraint attribute_to_gms foreign key (attribute_id) references abe_attribute (id);
alter table attribute_to_gm add index attributes_to_gm (gm_id), add constraint attributes_to_gm foreign key (gm_id) references abe_group_gm (id);
