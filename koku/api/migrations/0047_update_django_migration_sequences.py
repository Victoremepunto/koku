# Generated by Django 3.1.10 on 2021-05-13 21:31
import logging

from django.db import migrations


LOG = logging.getLogger(__name__)


def update_sequences(apps, schema_editor):
    all_sequences_sql = """
select nsp.nspname as "namesp",
       tab.relname as "tabname",
       seq.relname as "seqname",
       seq.oid as "seqoid"
  from pg_class as seq
  join pg_depend as dep
    on seq.relfilenode = dep.objid
   and dep.deptype = 'a'
  join pg_class as tab
    on dep.refobjid = tab.relfilenode
  join pg_namespace nsp
    on nsp.oid = tab.relnamespace
  join public.api_tenant tn
    on tn.schema_name = nsp.nspname
 where tab.relname = 'django_migrations'
   and (nsp.nspname = 'template0' or
        nsp.nspname ~ '^acct')
 order
    by nsp.nspname desc;
"""
    max_pk_val = """
select max(id)
  from "{}"."{}";
"""
    update_sequence_sql = """
select setval(%s, %s);
"""

    conn = schema_editor.connection
    with conn.cursor() as cur:
        LOG.info("Collecting sequence information...")
        cur.execute(all_sequences_sql)
        cols = [d.name for d in cur.description]
        res = [dict(zip(cols, rec)) for rec in cur.fetchall()]

        for rec in res:
            LOG.info("Getting max pk value from the django_migrations table...")
            cur.execute(max_pk_val.format(rec["namesp"], rec["seqname"]))
            new_sequence_val = (cur.fetchone() or [1])[0]

            LOG.info(
                f"Setting sequence {rec['namesp']}.{rec['seqname']} ({rec['seqoid']}) value to {new_sequence_val}"
            )
            cur.execute(update_sequence_sql, (rec["seqoid"], new_sequence_val))


class Migration(migrations.Migration):

    dependencies = [("api", "0046_jsonb_sha256_text")]

    operations = [migrations.RunPython(update_sequences)]
